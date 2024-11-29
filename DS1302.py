from machine import Pin
from time import time, sleep



class RTC:
    WRITE_SECOND_ADDR = 0x80
    WRITE_MINUTES_ADDR = 0x82
    WRITE_HOURS_ADDR = 0x84
    WRITE_DAY_ADDR = 0x86
    WRITE_MONTH_ADDR = 0x88
    WRITE_DAY_OF_WEEK_ADDR = 0x8A
    WRITE_YEAR_ADDR = 0x8C
    WRITE_WP_ADDR = 0x8E

    READ_SECOND_ADDR = 0x81
    READ_MINUTES_ADDR = 0x83
    READ_HOURS_ADDR = 0x85
    READ_DAY_ADDR = 0x87
    READ_MONTH_ADDR = 0x89
    READ_DAY_OF_WEEK_ADDR = 0x8B
    READ_YEAR_ADDR = 0x8D
    READ_WP_ADDR = 0x8F
    
    DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    def __init__(self, clk=1, data=2, reset=3):
        self.CLK_PIN = clk
        self.DATA_PIN = data
        self.RST_PIN = reset
        self.clk = Pin(clk, Pin.OUT)
        self.data = Pin(data, Pin.OUT)
        self.rst = Pin(reset, Pin.OUT)

    def set_output(self, pins:str):
        """change pin to output
            pin:str -> available options: 'clk', 'data', 'rst',
            or string like 'clk data rst' to change a few pins"""
        result = False
        if 'clk' in pins:
            self.clk = Pin(self.CLK_PIN, Pin.OUT)
            result = True
        if 'data' in pins:
            self.data = Pin(self.DATA_PIN, Pin.OUT)
            result = True
        if 'rst' in pins :
            self.rst = Pin(self.RST_PIN, Pin.OUT)
            result = True
        return result

    def set_input(self, pins:str):
        """change pin to input
            pin:str -> available options: 'clk', 'data', 'rst',
            or string like 'clk data rst' to change a few pins"""
        result = False
        if 'clk' in pins:
            self.clk = Pin(self.CLK_PIN , Pin.IN)
            result = True
        if 'data' in pins:
            self.data = Pin(self.DATA_PIN, Pin.IN)
            result = True
        if 'rst' in pins :
            self.rst = Pin(self.RST_PIN, Pin.IN)
            result = True
        return result
    
    def set_data_pin_input(self):
        self.set_input('data')
        
    def set_data_pin_output(self):
        self.set_output('data')
        
    def send_bit(self, val):
        self.data.value(val)
        self.clk.on()
        self.clk.off()
        
    def read_bit(self):
        self.clk.off()
        val = self.data.value()
        self.clk.on()
        return val
    
    def rev_str(self, s):
        return "" if not(s) else self.rev_str(s[1::])+s[0]
    
    def read_data(self, addr="10000001"):
        #reverse order, first LSB sent
        addr = self.rev_str(addr)
        self.clk.off()
        self.rst.on()
        
        [self.send_bit(int(bit)) for bit in addr]
        
        self.set_data_pin_input()
        
        read_data =  [self.read_bit() for _ in range(8)]
            
        self.rst.off()
        self.clk.off()
        self.set_data_pin_output()
        #reverse order becaus recived LSB first 
        return read_data[::-1]
    
    def write_data(self, addr="10000000", data="00000000"):
        #reverse order , first LSB sent
        addr = self.rev_str(addr)
        data = self.rev_str(data)
        
        self.clk.off()
        self.rst.on()
        
        [self.send_bit(int(bit)) for bit in addr+data]
        
        self.rst.off()
        self.clk.off()
    
    def convert_to_send_format(self, data:int):
        """convert data in which tens and ones are written separatley"""
        tens = data//10
        single = data%10
        #separate tens in first 4 bits and singel in last 4 bits
        converted = (0x00|tens<<4)|single
        #convert to bin string and cut '0b' prefix
        conv_to_bin = bin(converted)[2:]
        #fill missing '0' to len of byte
        n = 8 - len(conv_to_bin)
        return n*'0'+conv_to_bin
    
    def convert_list_bin_to_int(self, data):
        data_int = 0x00
        for d in data:
            data_int <<= 1
            data_int |= d
        return data_int
    
    def write_seconds(self, data):
        addr = bin(RTC.WRITE_SECOND_ADDR)[2:]
        data = self.convert_to_send_format(data)
        self.write_data(addr, data)
        
    def write_minutes(self, data):
        addr = bin(RTC.WRITE_MINUTES_ADDR)[2:]
        data = self.convert_to_send_format(data)
        self.write_data(addr, data)
    
    def write_hours(self, data):
        addr = bin(RTC.WRITE_HOURS_ADDR)[2:]
        data = self.convert_to_send_format(data)
        self.write_data(addr, data)
        
    def write_time(self, hours, minutes, second=0):
        self.write_hours(hours)
        self.write_minutes(minutes)
        self.write_seconds(second)
        
    def write_day(self, data):
        addr = bin(RTC.WRITE_DAY_ADDR)[2:]
        data = self.convert_to_send_format(data)
        self.write_data(addr, data)

    def write_month(self, data):
        addr = bin(RTC.WRITE_MONTH_ADDR)[2:]
        data = self.convert_to_send_format(data)
        self.write_data(addr, data)
    
    def write_day_of_week(self, data):
        addr = bin(RTC.WRITE_DAY_OF_WEEK_ADDR)[2:]
        data = self.convert_to_send_format(data)
        self.write_data(addr, data)
        
    def write_year(self, data):
        addr = bin(RTC.WRITE_YEAR_ADDR)[2:]
        data = self.convert_to_send_format(data)
        self.write_data(addr, data)
        
    def write_date(self, day:int, month:int, year:int):
        """set date
            day:int
            month:int
            year: int -> only last 2 digits of year"""
        self.write_day(day)
        self.write_month(month)
        self.write_year(year)
        
    def read_seconds(self):
        addr = bin(RTC.READ_SECOND_ADDR)[2:]
        data = self.read_data(addr=addr)
        sec10 = self.convert_list_bin_to_int(data[1:4])
        sec = self.convert_list_bin_to_int(data[4:])
        return str(sec10) + str(sec)
    
    def read_minutes(self):
        addr = bin(RTC.READ_MINUTES_ADDR)[2:]
        data = self.read_data(addr=addr)
        min10 = self.convert_list_bin_to_int(data[1:4])
        min_ = self.convert_list_bin_to_int(data[4:])
        return str(min10) + str(min_)
    
    def read_hour(self):
        """return hour strin defalut in 24h mode"""
        addr = bin(RTC.READ_HOURS_ADDR)[2:]
        data = self.read_data(addr=addr)
        hour10 = self.convert_list_bin_to_int(data[2:4])
        hour = self.convert_list_bin_to_int(data[4:])
        return str(hour10) + str(hour)
    
    def read_time(self):
        return self.read_hour()+":"+self.read_minutes()+":"+self.read_seconds()
    
    def read_day(self):
        addr = bin(RTC.READ_DAY_ADDR)[2:]
        data = self.read_data(addr=addr)
        day10 = self.convert_list_bin_to_int(data[2:4])
        day = self.convert_list_bin_to_int(data[4:])
        return str(day10) + str(day)
    
    def read_month(self):
        addr = bin(RTC.READ_MONTH_ADDR)[2:]
        data = self.read_data(addr=addr)
        month10 = self.convert_list_bin_to_int(data[3:4])
        month = self.convert_list_bin_to_int(data[4:])
        return str(month10) + str(month)
    
    def read_day_of_week(self):
        addr = bin(RTC.READ_DAY_OF_WEEK_ADDR)[2:]
        data = self.read_data(addr=addr)
        day = self.convert_list_bin_to_int(data[5:])
        return RTC.DAYS_OF_WEEK[day-1]
    
    def read_year(self):
        addr = bin(RTC.READ_YEAR_ADDR)[2:]
        data = self.read_data(addr=addr)
        year10 = self.convert_list_bin_to_int(data[:4])
        year = self.convert_list_bin_to_int(data[4:])
        return "20" + str(year10) + str(year)
    
    def read_date(self):
        day = self.read_day()
        month = self.read_month()
        year = self.read_year()
        return day+'.'+month+'.'+year
                
                        
    
def test_func():
    rtc = RTC()
    print(rtc.read_date())
    print(rtc.read_time())

    
if __name__ == "__main__":
    main()
    