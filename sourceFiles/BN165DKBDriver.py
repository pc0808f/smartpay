import utime
#=========================================
#读取指定位数的键盘码(每一级8位)
#基于74HC165
def readKBData(
    chipCount,   #级联74HC165数量
    CP,          #时钟管脚
    CE,          #时钟使能管脚
    PL,          #并行输入/锁定数据管脚
    Q7           #顶级串行输出管脚
): 
    #串行数据列表
    data=[]
    #每次读取前
    #清空数据列表
    data.clear()
    #CE高电平时钟禁用
    CE.value(1)
    #PL低电平以并行输入
    PL.value(0)
    #休眠1ms给数据输入时间
    utime.sleep_ms(1)
    #然后PL高电平锁定并行数据
    PL.value(1)
    #CE低电平时钟启用
    CE.value(0)
    #CP低电平
    CP.value(0)
    #读入第一位串行数据
    data.append(Q7.value());
    #循环读入后7位数据
    for i in range(chipCount*8-1):
        CP.value(1)
        data.append(Q7.value());
        CP.value(0)
        utime.sleep_ms(1)
    return data
#=========================================

#将串行数据中每个值为1的位翻译为指定键含义字符串的方法
def parseKeyData(keyData,meaningStrList):
    #返回结果
    result=[]
    #键码比特数
    count=len(keyData)
    #遍历键码中的每个比特
    for i in range(count):
        #若对应比特位为1则将对应键含义字符串放入结果列表
        if(keyData[i]==1):
            result.append(meaningStrList[i])
    return result
    
