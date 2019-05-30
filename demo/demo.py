#!/usr/bin/env python3
# __*__ coding:utf-8 __*__
# author: wangpengtai
# email: wangpengtai@163.com
# date: 2019528

import logging
from ldap3 import Reader, ObjectDef, Server, Connection, ALL, Writer
from ldap3.utils.log import set_library_log_detail_level, BASIC
from ops_ldap.config import config


# ldap的操作方法，增删改查
class LdapManage:
    def __init__(self, **ldap_init):
        # 初始化参数
        self.__ldap_url = ldap_init['ldap_url']
        self.__ldap_dn = ldap_init['ldap_dn']
        self.__ldap_pass = ldap_init['ldap_pass']
        LdapManage.__Connect(self)
        LdapManage.__Logging(self)

    # 生成操作日志
    def __Logging(self, loglocation='logs'):
        logging.basicConfig(filename=loglocation + '/' + 'client_application.log', level=logging.DEBUG)
        set_library_log_detail_level(BASIC)

    # 连接ldap服务器
    def __Connect(self):
        self.server = Server(self.__ldap_url, get_info=ALL)
        self.conn = Connection(self.server, self.__ldap_dn, self.__ldap_pass, auto_bind=True)

    # 激活读游标
    def __ReaderCursor(self, Domain, user=''):
        obj_person = ObjectDef(config.Filter[Domain], self.conn)
        # obj_person = ObjectDef(['person', 'posixAccount', 'top'], self.conn)
        result = Reader(self.conn, obj_person, Domain, user)
        return result

    # 激活写游标
    def __WriteCursor(self, Domain):
        r = LdapManage.__ReaderCursor(self, Domain)
        r.search()
        return Writer.from_cursor(r)

    # 类方法模糊查询用户
    def EntryMap(self, Domain):
        r = LdapManage.__ReaderCursor(self, Domain)
        r_list = r.search()
        for person in r_list:
            print(person.entry_to_ldif())

    # 类方法精确查询用户
    # usage: user_selectd
    # 书写格式: "cn:=ops_ldap"
    def EntryInfo(self, user_dn, Domain):
        if LdapManage.__EntryExist(self, user_dn, Domain):
            r = LdapManage.__ReaderCursor(self, Domain, user_dn)
            r.search()
            r_list = r.match_dn(user_dn)
            print(f'{user_dn} 的ldif格式信息，\n如下：')
            print(r_list[0].entry_to_ldif())
        else:
            print(f'{user_dn} 不存在！')

    # 匹配到查询重复用户
    ##r.match  r.match_dn
    ###r.match_dn(dn)
    ###r.match(attributes, value)
    # newuser格式：test即可
    def __EntryExist(self, user_dn, Domain='ou=People,dc=sensoro,dc=com'):
        r = LdapManage.__ReaderCursor(self, Domain)
        r.search()
        if r.match_dn(user_dn):
            return True

    # 插入条目，使用Write光标加载Read光标后，获取可写的条目列表
    def EntryInsert(self, Domain, **userinfo):
        # 查看用户是否存在
        if LdapManage.__EntryExist(self, userinfo['dn'], Domain):
            print(f'{dn} 已经存在了！\n'.format(**userinfo))
            LdapManage.EntryInfo(self, userinfo['dn'], Domain)
        else:
            # 用户不存在，写入用户信息
            w = LdapManage.__WriteCursor(self, Domain)
            # uidnumber根据用户总个数自己累加
            userinfo['uidnumber'] = len(w) + 1000

            # 插入新用户的dn
            entry_item = w.new(userinfo['dn'])

            # 采用迭代方式插入其他属性信息
            for key, value in userinfo.items():
                if key is 'dn' or key is 'tag':
                    continue
                else:
                    entry_item[key] = value
            # 提交操作
            if entry_item.entry_commit_changes():
                print(f"{userinfo['dn']} 添加成功！")
                LdapManage.EntryInfo(self, userinfo['dn'], Domain)
            else:
                print(f"{userinfo['dn']} 添加失败！")

    def __MemberInGroupExsit(self, user_tag, user_dn, Domain):
        w = LdapManage.__WriteCursor(self, Domain)
        for group in w:
            if user_tag in group.entry_dn:
                if user_dn in group.entry_attributes_as_dict['uniqueMember']:
                    return True
                break

    # 将用户添加到相应的应用组中
    def AddMemberToGroup(self, user_tag, user_dn, Domain='ou=Group,dc=sensoro,dc=com'):
        if LdapManage.__EntryExist(self, user_dn, 'ou=People,dc=sensoro,dc=com'):
            if LdapManage.__MemberInGroupExsit(self, user_tag, user_dn, Domain):
                print(f'{user_dn}已存在组内')
            else:
                w = LdapManage.__WriteCursor(self, Domain)
                for group in w:
                    if user_tag in group.entry_dn:
                        group.uniqueMember += user_dn
                    group.entry_commit_changes()
                print(f'{user_dn} 添加应用组成功！')
        else:
            print(f'{user_dn} 不存在，请先创建用户！')

    def DeleteMemberFromGroup(self, user_tag, user_dn, Domain='ou=Group,dc=sensoro,dc=com'):
        if not LdapManage.__EntryExist(self, user_dn, 'ou=People,dc=sensoro,dc=com'):
            print(f'{user_dn} 不存在')
        else:
            if LdapManage.__MemberInGroupExsit(self, user_tag, user_dn, Domain):
                w = LdapManage.__WriteCursor(self, Domain)
                for group in w:
                    if user_tag in group.entry_dn:
                        group.uniqueMember -= user_dn
                    group.entry_commit_changes()
                print(f'{user_dn} 从应用组删除成功！')
            else:
                print(f'{user_dn} 不在应用组！')

    # 查询用户所在组列表
    def __MemberOfViewExsit(self, user_dn, Domain):
        r = LdapManage.__ReaderCursor(self, Domain)
        e = r.search()
        # print(type(e))
        for i in e:
            if user_dn in i.entry_attributes_as_dict['uniqueMember']:
                return True

    def MemberOfView(self, user_dn, Domain='ou=Group,dc=sensoro,dc=com'):
        if LdapManage.__EntryExist(self, user_dn, 'ou=People,dc=sensoro,dc=com'):
            if LdapManage.__MemberOfViewExsit(self, user_dn, Domain):
                r = LdapManage.__ReaderCursor(self, Domain)
                e = r.search()
                for i in e:
                    if user_dn in i.entry_attributes_as_dict['uniqueMember']:
                        print(i.entry_to_ldif())
            else:
                print(f'{user_dn} 不存在各个应用组中!')
        else:
            print(f'{user_dn} 不存在！')

    # 删除选定条目
    def EntryDelete(self, userdn, Domain):
        if LdapManage.__EntryExist(self, userdn):
            w = LdapManage.__WriteCursor(self, Domain)
            k = w.match_dn(userdn)
            k[0].entry_delete()
            k[0].entry_commit_changes()
            print(f'{userdn} 已经删除！')
        else:
            print("没有用户可以删除！")


# 连接ldap服务器的基础信息
# ldap_init = {
#
#     'ldap_url': '192.168.56.103',
#     'ldap_dn': 'cn=root,dc=sensoro,dc=com',
#     'ldap_pass': '123456',
#     'base_dc': 'ou=People,dc=sensoro,dc=com'
# }

# if __name__ == '__main__':
# 用户的必要类属性的列表

# # 构造新用户的必要信息
# userinfo = {
#     'tag': 'ops',
#     'dn': 'cn=new_test3,ou=People,dc=sensoro,dc=com',  # 更改cn即可
#     'sn': 'new_test3',
#     'uid': 'new_test3@sensoro.com',
#     'uidnumber': '',  # 为空即可uid函数自动添加
#     'homedirectory': '/home/' + 'new_test3',  # /home不更改
#     'gidNumber': '1000'  # 不用更改
# # }
# ops_ldap = LdapManage(**ldap_init)
# # ops_ldap.EntryInfo('wangpeng','ou=People,dc=sensoro,dc=com')
# # ops_ldap.EntryInsert(**userinfo)
# # ops_ldap.EntryDelete('new_test')
# # ops_ldap.EntryInfo('new_test')
# user_tag = ['nodejs', 'ops', 'python', 'qa', 'web', 'admin']
# app_tag = ['gitlab', 'jenkins', 'jumpserver']

# test eg:
# ops_ldap.EntryMap('ou=Group,dc=sensoro,dc=com')
# ops_ldap.EntryDelete('cn=new_test2,ou=People,dc=sensoro,dc=com','ou=People,dc=sensoro,dc=com')
# ops_ldap.EntryInsert('ou=People,dc=sensoro,dc=com',**userinfo)
# ops_ldap.EntryInfo('cn=new_test4,ou=People,dc=sensoro,dc=com','ou=People,dc=sensoro,dc=com')
# ops_ldap.MemberOfView('cn=new_test2,ou=People,dc=sensoro,dc=com')
# ops_ldap.AddMemberToGroup('ops','cn=new_test3,ou=People,dc=sensoro,dc=com')
# ops_ldap.DeleteMemberFromGroup('ops','cn=new_test2,ou=People,dc=sensoro,dc=com')
# ops_ldap.MemberOfView('cn=new_test2,ou=People,dc=sensoro,dc=com')
