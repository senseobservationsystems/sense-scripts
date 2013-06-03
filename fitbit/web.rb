require 'mechanize'
require 'nokogiri'
require 'commonsense-ruby-lib'
require 'json'




####################
# Main function, automatically called when run from command line (see bottom of script)
#####################

def main(sy,sm,sd,ey,em,ed,settings_file="settings.yaml")
    settings = YAML.load_file(settings_file)
    
    sdate = DateTime.new(sy,sm,sd)
    edate = DateTime.new(ey,em,ed)

    agent = login_fitbit(settings["fitbit_user"],settings["fitbit_pass"])
    
    days = period_with_data(sdate,edate,agent,settings)
    data = data_for_days( days, agent, settings )
    

    #data_to_file( data, "fitbit_3.json")
    send_to_cs( data, settings ) 
end


####################
# Setup mechanize and login 
#####################

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


####################
# Following three functions get actual data, but need a list of days to work
####################

def data_for_days(days,agent,settings)
    (days.map do |d| 
        data_for_day(d,agent,settings)
    end).flatten
end


def data_for_day(d,agent,settings)
    
    date_str =  d.strftime('%Y-%-m-%-d')

    xmlpage = agent.get('http://www.fitbit.com/graph/getGraphData?'+
                'userId='+settings['fitbit_id']+
                '&type=intradaySleep&period=1d&dataVersion=871&version=amchart&'+
                'dateFrom='+date_str+'&dateTo='+date_str+'&chart_type=column2d')
    agent.back

    return parse_fitbit_xml(xmlpage,d)
end


def parse_fitbit_xml(xml,d)
    ret = []

    items = xml.search('/settings/data/chart/graphs/graph/value')
    start_time = DateTime.parse( items.first['description'].split.last, '%H:%M%p')
    
    d -= 1 if start_time.hour > 12 
      
    # dirty hack, probably there is a more graceful way to handle timezones
    # only thing i could find was rails specific
    #if d > DateTime.new( 2013, 3, 31, 2, 0 )
        # tz_off = '+2'
    # else
        # tz_off = '+1'
    # end

    #start_datetime = DateTime.new( d.year, d.month, d.day, 
                                  # start_time.hour, start_time.minute, 0, tz_off )
    start_time_local = Time.local( d.year, d.month, d.day, start_time.hour, start_time.minute)

    sec = start_time_local.to_time.to_i

    items.each do |x| 
        ret << { value:x.text.to_i, date:sec }
        sec+=60
    end
    
    return ret
end

####################
# Following two functions get a list of days for which data is available
####################

def period_with_data(sdate,edate,agent,settings)
    
    #we only retrieve data for whole months, so change start date to first of month
    nsdate = sdate
    nsdate -= ( sdate.day + 1 ) if sdate.day > 1

    days = []
    ((nsdate..edate).select { |d| d.day == 1 }).map do |d|
        days << days_with_data(d,agent,settings)
    end
    days.flatten!(1) 
    days.map! { |a| DateTime.new(*a) }
    days.reject! { |d| d < sdate or d > edate }

    return days
end

def days_with_data(d,agent,settings)
    date_str = d.strftime('%Y-%-m-%-d')
    
    dates = []

    page = agent.get('http://www.fitbit.com/graph/getGraphData?'+
            'userId='+settings['fitbit_id']+
            '&type=timeAsleepTotal&period=1m'+
            '&dataVersion=881&version=amchart&dateTo=' + date_str +
            '&ts=' + (DateTime.now.to_time.to_i * 1000).to_s +
            '&chart_type=column2d')
    
    page.search('//data/chart/graphs/graph/value').each do |x|
        dates << x['url'].split('/').pop(3).map(&:to_i) if x.text.to_f > 0.0
    end
    
    agent.back

    return dates 
end

####################
# Send data to commonSense 
####################

def send_to_cs(data, settings)
    # sensor id: 327992
    # pp data
    client = CommonSense::Client.new
    client.login( settings["cs_user"].to_s, settings["cs_pass"].to_s ) 
    
    while data.any? do
        client.session.post( '/sensors/' + settings['cs_sensor_id'].to_s + '/data.json', { :data => data.shift(1000) } )
    end

    return client.session.response_code
end



####################
# misc functions
#####################

def data_to_file(data,filename)
    #data = data_for_period(2012,12,2013,4)
    File.open(filename,'w') do |f| 
        f.write(data.to_json) 
    end
end


####################
# Automatically run script when called from commandline 
####################


if __FILE__ == $0
    
    if ARGV.count < 6 then
        abort "wrong number of parameters, usage: "+$0+" startyear startmonth startday endyear endmonth endday (settings_file)"
    end
    print "Importing your fitbit data..."
    sfile  = ARGV.pop
    main(*(ARGV.map(&:to_i)),sfile)
    print " done\n"
end
