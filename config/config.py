ldap_init = {
    'ldap_url': '192.168.56.103',
    'ldap_dn': 'cn=root,dc=sensoro,dc=com',
    'ldap_pass': '123456',
}

Filter = {
    'ou=People,dc=sensoro,dc=com': ['person', 'posixAccount', 'top'],
    'ou=Group,dc=sensoro,dc=com': ['groupOfUniqueNames', 'top']
}


#demo_ldap.LdapManage
# 用户的必要类属性的列表
Objectclass_People_list = ['person', 'posixAccount', 'top']

Objectclass_Group_list = ['groupOfUniqueNames', 'top']


#日志位置
log = 'logs'
