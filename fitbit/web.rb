require 'mechanize'
require 'nokogiri'
require 'commonsense-ruby-lib'
require 'json'

    

def login_fitbit(fb_user,fb_pass)
    a = Mechanize.new { |agent|
        agent.user_agent_alias = 'Mac Safari'
    }

    a.get('https://www.fitbit.com/login') do |page|
       
        dash_page = page.form_with(:action => 'https://www.fitbit.com/login') do |f|
            f.email = fb_user 
            f.password = fb_pass 
        end.click_button
    end
    
    return a
end

def load_data(y,m,d,fb_user,fb_pass,fb_id)

    date_str = y.to_s+'-'+m.to_s+'-'+d.to_s
    creds = IO.read('credentials.txt').split

    a = Mechanize.new { |agent|
        agent.user_agent_alias = 'Mac Safari'
    }

    a.get('https://www.fitbit.com/login') do |page|
       
        dash_page = page.form_with(:action => 'https://www.fitbit.com/login') do |f|
            f.email = creds[0]
            f.password = creds[1]
        end.click_button
        
        a.get('http://www.fitbit.com/graph/getGraphData?'+
                'userId=24Y4CV&type=intradaySleep&period=1d&dataVersion=871&version=amchart&'+
                'dateFrom='+date_str+'&dateTo='+date_str+'&chart_type=column2d',[],dash_page) do |graph_page|
            return parse_fitbit_xml(graph_page,y,m,d)
        end
    end
end

def parse_fitbit_xml(xml,y,m,d)
    ret = []

    items = xml.search('/settings/data/chart/graphs/graph/value')
    start_time = DateTime.parse( items.first['description'].split.last, '%H:%M%p')
    
    d = DateTime.new(y,m,d)
    d -= 1 if start_time.hour > 12 
    sec = d.to_time.to_i

    items.each do |x| 
        ret << { value:x.text.to_i, date:sec }
        sec+=60
    end
    
    return ret
end

def days_with_data(d,agent,settings)
    date_str = d.strftime('%Y-%-m-%-d')
    
    dates = []

    page = agent.get('http://www.fitbit.com/graph/getGraphData?'+
            'userId='+settings['fitbit_id']+
            '&type=timeAsleepTotal&period=1m'+
            '&dataVersion=881&version=amchart&dateTo=' + date_str +
            '&ts=' + (DateTime.now.to_time.to_i * 1000).to_s +
            '&chart_type=column2d',[],dash_page)
    
    page.search('//data/chart/graphs/graph/value').each do |x|
        dates << x['url'].split('/').pop(3).map(&:to_i) if x.text.to_f > 0.0
    end
    
    agent.back

    return dates 

    
    # a = Mechanize.new { |agent|
    #     agent.user_agent_alias = 'Mac Safari'
    # }

    # a.get('https://www.fitbit.com/login') do |page|
    #    
    #     dash_page = page.form_with(:action => 'https://www.fitbit.com/login') do |f|
    #         f.email = creds[0]
    #         f.password = creds[1]
    #     end.click_button
    #     
    #     a.get('http://www.fitbit.com/graph/getGraphData?userId=24Y4CV&type=timeAsleepTotal&period=1m&'+
    #             'dataVersion=881&version=amchart&dateTo=' + date_str +
    #             '&ts=' + (DateTime.now.to_time.to_i * 1000).to_s +
    #             '&chart_type=column2d',[],dash_page) do |month_graph|
    #         # pp month_graph
    #         month_graph.search('//data/chart/graphs/graph/value').each do |x|
    #             dates << x['url'].split('/').pop(3).map(&:to_i) if x.text.to_f > 0.0
    #         end
    #     end
    #     return dates
    # end
end

def period_with_data(sdate,edate,agent,settings)
    
    #we only retrieve data for whole months, so change start date to first of month
    nsdate = sdate - sdate.day if sdate.day > 1
    days = []

    (nsdate..edate).select { |d| d.day == 1 }).map do |d|
        days << days_with_data(d,agent,settings)
    end

    days.reject! {|a|

    ((Date.new(sy, sm)..Date.new(ey, em)).select {|d| d.day == 1}).each do |d|
        days.concat days_with_data(d.year,d.month)
    end
    return days
end

def data_for_period(sy,sm,sd,ey,em,ed)
    sdate = DateTime.new(sy,sm,sd)
    edate = DateTime.new(ey,em,ed)

    data = []
    
    period_with_data(sy,sm,ey,em).map do |d|
        cdate = DateTime.new *d
        if cdate >= sdate and cdate <= edate then
            data.concat load_data *d
        end
    end

    return data
end


def data_to_file()
    data = data_for_period(2012,12,2013,4)
    File.open('fitbit.json','w') do |f| 
        f.write(data.to_json) 
    end
end


def send_to_cs(data)
    # sensor id: 327992
    client = CommonSense::Client.new
    client.login( *(IO.read('cs_cred.txt').split) ) 
    client.session.post( '/sensors/327992/data.json', { :data => data } )
    return client.session.response_code
end

def main(sy,sm,sd,ey,em,ed,settings_file="settings.yaml")
    settings = YAML.load_file(settings_file)
    
    sdate = DateTime.new(sy,sm,sd)
    edate = DateTime.new(ey,em,ed)

    agent = login_fitbit(settings["fitbit_user"],settings["fitbit_pass"])
    
    days_with_data = 

    # send_to_cs( JSON.parse(IO.read('fitbit.json')) )
    send_to_cs( data_for_period
end

if __FILE__ == $0
    
    if ARGV.count < 6 then
        abort "wrong number of parameters, usage: "+$0+" startyear startmonth startday endyear endmonth endday (settings_file)"
    end

    main(*ARGV)
end
