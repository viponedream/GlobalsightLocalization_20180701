#!/usr/bin/env python    
# -*- coding: utf-8 -*

"""
作者：易可可
创建日期：2018年6月25日
最后更新日期：2018年7月1日
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
代码功能：
本文件是一段 python 3 代码，
调用有道翻译api和微软必应翻译api将“LocaleResource_en_US.properties”文件里的待本地化的英文翻译为中文，
程序将使用正则表达式提取出文件中需要翻译的部分，调用机器翻译后将翻译结果写入另一文件"LocaleResource_zh_CH.properties"中。
"""

#调用翻译api需要
import urllib.request
import json
import time
import hashlib

#导入机器翻译功能模块：必应翻译和有道翻译
import machine_translation.youdaofanyi as youdao
import machine_translation.bingfanyi as bing

#使用正则表达式需要
import re

#sys模块包含了与Python解释器和它的环境有关的函数。
import sys


def regex(content,pattern):  
    #@description:处理待翻译文件用到的六个正则表达式
    #@return:根据不同的正则表达式返回是否匹配到结果
    if pattern == 1:
        pattern1 = re.compile(r'DO NOT TRANSLATE THIS SECTION')  #匹配是否有‘DO NOT TRANSLATE THIS SECTION’
        search1 = pattern1.search(content)  #search方法匹配部分内容
        return search1
    elif pattern == 2:
        pattern2 = re.compile(r'#.*')  #匹配是否含‘#’号
        search2 = pattern2.search(content)
        return search2
    elif pattern == 3:
        pattern3 = re.compile(r'([^=]*)(=\s*)(.*)')  #括号代表分组，有三组：第一组匹配非等号的符号0次或多次；第二组匹配等号和右边的空格（0个或多个）；第三组匹配任意除换行符“\n”外的字符0次或多次。
        search3 = pattern3.search(content)     
        return search3
    elif pattern == 4: #匹配不在“DO NOT TRANSLATE THIS SECTION”区域里的行尾是'.htm'的行
        pattern4 = re.compile(r'(\.htm)(.*)') #匹配是否在'DO NOT TRANSLATE THIS SECTION'区域之外含有'.htm'以及在'.htm'后有无字符
        search4 = pattern4.search(content)
        return search4
    elif pattern == 5:
        pattern5 = re.compile(r'<.*>') #匹配是否含标签
        search5 = pattern5.search(content)
        return search5
    elif pattern == 6:  #匹配是否含'termbase‘或’Termbase'两个词
        pattern6 = re.compile(r'termbase|Termbase') 
        search6 = pattern6.search(content)
        return search6

def fanyi (text, api):
    #@description:选择调用两个翻译api
    #@return:返回api翻译结果
    if api == "bing":
        translator = bing.BingFanyi("zh")
        translation_result = translator.translate(text) #翻译结果
        return translation_result
    elif api == "youdao":
        translator = youdao.YouDaoFanyi("zh")
        translation_result = translator.translate(text) #翻译结果  
        return translation_result
    else:
        return 0

def termbase_replace (result):
    #@description:翻译api没法翻译termbase和Termbase两个术语，此函数手动对机翻结果进行替换
    #@return:传入的内容含termbase或Termbase，则返回替换后的结果；不含则返回原内容
    if regex(result,6) is not None:
        final_result = result.replace("termbase","术语库")
        final_result = result.replace("Termbase","术语库")
        return final_result
    else:
        return result
    
   
if __name__ == '__main__':     
    #@description:主程序，实现对LocaleResource_en_US.properties文件的自动机器翻译
    #@print:由于程序调用api超5000次，运行耗时过长，为追踪程序进程，程序会打印出翻译api已翻译行数，以及在最后分别打印调用必应翻译api和有道翻译api的总次数。
    
    with open('test.txt') as file: #测试用
    #with open('LocaleResource_en_US.properties') as file: #打开待翻译文件，默认模式为‘r’，只读模式
            lines = file.readlines()      #读取文件全部内容
            record = 0    #由于待翻译文件较长，程序调用api超5000次，为追踪程序进程，定义record变量记录程序调用api已经翻译了多少行。
            bingtimes = 0  #储存必应api调用次数
            youdaotimes = 0  #储存有道api调用次数
            print("翻译api已翻译行数：")
            
            with open ("result.txt","a") as f:  #测试用
            #with open ("LocaleResource_zh_CH.properties","a") as f:  #机翻结果写入文件,‘a’为追加写入模式
                f.seek(0)  #把文件定位到position 0，没有这句的话，文件是定位到数据最后，则下一行truncate方法没法执行清空文件的操作
                f.truncate() #清空文件
                flag = 0   #flag初始值为0
                for line in lines:     #遍历所有行
                    if flag == 1: #flag=1时，证明该行属于不需要翻译的部分。
                        search2 = regex(line,2) #调用正则表达式pattern2，判断该行是否有'#'
                        if search2 is None:  #该行没有'#'，直接将该行打印
                            f.write(line)
                        else:    #该行有'#'，直接写入文件并将flag赋值为0，该行后不再是不需要翻译的部分
                            f.write(line)
                            flag = 0
                    else:  #flag=0时，判断该行有无“DO NOT TRANSLATE THIS SECTION”字样
                        search1 = regex(line,1)  #调用正则表达式pattern1，判断该行是否有'DO NOT TRANSLATE THIS SECTION'
                        if search1 is not None:    #该行有“DO NOT TRANSLATE THIS SECTION”，直接将该行写入文件，并将flag赋值为1
                                f.write(line)
                                flag = 1
                                continue        #循环到下一行
                        
                        else:  #该行没有“DO NOT TRANSLATE THIS SECTION”
                            search3 = regex(line,3)  #调用正则表达式pattern3，判断该行是否有'([^=]*)(=\s*)(.*)'，类似于"A=B"的结构
                            if search3 is None or search3.group(3) is '':  #该行没有匹配到类似于"A=B"的结构，或者等号右边的内容为0个或多个空格，直接将该行写入文件
                                    f.write(line)
                                
                            else:    #如果该行匹配到类似于"A=B"的结构，进行匹配内容的翻译
                                search_result = search3.group(3)  #search3.group(3)代表'([^=]*)(=\s*)(.*)'分组的第三组，即等号右边待翻译的内容
                                search4 = regex(search_result,4)  #调用正则表达式pattern4，判断该行是否有'.htm'及'.htm'后有无字符
                                if search4 is not None and search4.group(2) is '':  #该行有'.htm'且'.htm'后无字符，则该行无需翻译，直接写入文件
                                    f.write(line)
                                else:  #该行没有'.htm'，继续匹配
                                    search5 = regex(line,5)  #调用正则表达式pattern5，判断该行是否有'<.*>'，即标签
                                    if search5 is not None:  #该行有标签
                                        bingtimes += 1  #调用必应翻译次数加1
                                        record += 1  #调用翻译api次数加1
                                        translation_result = fanyi(str(search_result),"bing")  #调用必应翻译，返回结果
                                        final_result = termbase_replace(translation_result)
                                        string_result = search3.group(1)+search3.group(2)+str(final_result)  #将翻译结果拼接到整行
                                        f.write(string_result+"\n")  #将string_result写入文件
                                        print(record)  #打印至今为止翻译api已翻译行数
                                    
                                    else:
                                        record += 1  #调用翻译api次数加1
                                        if record <= 2200:  # api调用有字数限制，必应翻译api默认只调用2200次
                                            bingtimes += 1  #调用必应翻译次数加1
                                            translation_result = fanyi(str(search_result),"bing") 
                                            final_result = termbase_replace(translation_result)
                                            string_result = search3.group(1)+search3.group(2)+str(final_result)  
                                            f.write(string_result+"\n")
                                            print(record)  #打印至今为止翻译api已翻译行数
                                        
                                        else:   #必应翻译api调用2200次后，开始调用有道翻译api
                                            youdaotimes += 1  #调用有道翻译次数加1
                                            translation_result = fanyi(str(search_result),"youdao") #调用有道翻译，返回结果  
                                            final_result = termbase_replace(translation_result)
                                            string_result = search3.group(1)+search3.group(2)+str(final_result) #将翻译结果拼接到整行
                                            f.write(string_result+"\n") 
                                            print(record)  #打印至今为止翻译api已翻译行数
                                                
                
    print("调用翻译必应api和有道api的总次数："+str(record))
    print("调用必应翻译api的总次数："+str(bingtimes))
    print("调用有道翻译api的总次数："+str(youdaotimes))
    
    f.close()    #关闭两个文件    
    file.close()