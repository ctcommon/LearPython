from PyLuaTblParser import *
a1 = PyLuaTblParser()
a2 = PyLuaTblParser()
a3 = PyLuaTblParser()


test_str = '{array = {65,23,5},dict = {mixed = {43,54.33,false,9,string = "value",},array = {3,6,4,},string = "value",},}'
a1.load(test_str)
d1 = a1.dump()
print d1
d1 = a1.dumpDict()
print d1

a2.loadDict(d1)

d2 = a2.dump()
print d2
file_path = "lua_table_test.lua"

#a2.dumpLuaTable(file_path)
a3.loadLuaTable(file_path)
d3 = a3.dump()
print d3
d3 = a3.dumpDict()
print d3
a3.loadDict(d3)
d3 = a3.dump()
print d3



	
