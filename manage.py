#!/usr/bin/env python3
# __*__ coding:utf-8 __*__

from ops_ldap.demo import demo
from ops_ldap.config import config


ldap_init = {

    'ldap_url': '192.168.56.103',
    'ldap_dn': 'cn=root,dc=sensoro,dc=com',
    'ldap_pass': '123456',
    'base_dc': 'ou=Group,dc=sensoro,dc=com'
}
# 构造新用户的必要信息
userinfo = {
    'tag': 'ops',
    'dn': 'cn=new_test,ou=People,dc=sensoro,dc=com',  # 更改cn即可
    'sn': 'new_test',
    'uid': 'new_test@sensoro.com',
    'uidnumber': '',  # 为空即可uid函数自动添加
    'homedirectory': '/home/' + 'new_test',  # /home不更改
    'gidNumber': '1000'  # 不用更改
}
Group_app = ['gitlab','jenkins','jumpserver']
Group_department = ['nodejs','ops','python','qa','web']


#test1.EntryInsert(**userinfo)
#test1.EntryMap('cn=People,dc=sensoro,dc=com')

test1 = demo.LdapManage(**config.ldap_init)
#test1.EntryInfo('cn=new_test,ou=People,dc=sensoro,dc=com','ou=People,dc=sensoro,dc=com')
test1.MemberOfView('cn=new_test2,ou=People,dc=sensoro,dc=com')
test1.EntryMap('ou=People,dc=sensoro,dc=com')
