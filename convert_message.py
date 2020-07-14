#coding=utf-8
import sys
import os
import time
import random
import string

import itchat
from itchat.content import TEXT
from itchat.content import *
GROUP_NAME_CONTEXT = '素材'


@itchat.msg_register([TEXT, PICTURE, SHARING, NOTE, ATTACHMENT, VIDEO, RECORDING], isGroupChat=True)
def group_text(msg):
    #print(msg)
    #print(msg['Type'])
    #print(msg)
    send_msg = False
    if not SEND_USER_ID and msg['FromUserName'] == SEND_GROUP_ID:
        send_msg = True
    elif not SEND_USER_ID and msg['ToUserName'] == SEND_GROUP_ID:
        send_msg = True
    elif msg['FromUserName'] == SEND_GROUP_ID and msg['ActualUserName'] == SEND_USER_ID:
        send_msg = True
    elif msg['FromUserName'] == msg['ActualUserName'] and msg['ToUserName'] == SEND_GROUP_ID and msg['FromUserName'] == SEND_USER_ID:
        send_msg = True
    if send_msg:
        # import pdb
        # pdb.set_trace()
        file_name = None
        print(msg['Type'])
        if msg['Type'] in [PICTURE, ATTACHMENT, VIDEO, RECORDING]:
            prefix_value = ''.join(random.sample(string.ascii_letters + string.digits, 8))
            file_name = prefix_value + msg['FileName']
            msg.download(file_name)
            print('Download %s:%s success' % (msg['Type'], msg['FileName']))
        for resev_group in RESEV_GROUPS:
            out = send_weixin_msg(msg, resev_group['group_id'], file_name)
            print(out)
            i = 0
            while True:
                if out['BaseResponse']['Ret'] == 0:
                    time.sleep(random.randint(2, 8))
                    break
                elif out['BaseResponse']['Ret'] == 1205:
                    time.sleep(random.randint(300, 600))
                    out = send_weixin_msg(msg, resev_group['group_id'], file_name)
                    i = i+1
                    print("---try again %s----" % str(i))
                else:
                    send_weixin_msg(msg, resev_group['group_id'], file_name)
                    break
        if msg['Type'] in [PICTURE, ATTACHMENT, VIDEO, RECORDING]:
            os.remove(file_name)
            #time.sleep(10)


def send_weixin_msg(msg, group_id, file_name=None):
    if msg['Type'] in [TEXT]:
        out = itchat.send_raw_msg(msg['MsgType'], msg['Content'], group_id)
        #time.sleep(5)
    elif msg['Type'] in [PICTURE, ATTACHMENT, VIDEO, RECORDING]:
        out = itchat.send('@%s@%s' % ({'Picture': 'img', 'Video': 'vid'}.get(
            msg['Type'], 'fil'), file_name), group_id)
        #time.sleep(10)
    else:
        print("%s message do not support!" % msg['Type'])
        out = {'BaseResponse': {'Ret': 0, 'ErrMsg': '', 'RawMsg': ''}}
    return out

def login():
    #itchat.auto_login()
    itchat.login()
    groups = []
    #ex_groups = itchat.search_chatrooms(name=GROUP_NAME_CONTEXT)
    ex_groups = itchat.get_chatrooms(update=True)
    for group in ex_groups:
        group_dict = {}
        group_dict['group_name'] = group['NickName']
        group_dict['group_id'] = group['UserName']
        group_mumbers = []
        members = itchat.update_chatroom(group['UserName'])['MemberList']
        for mumber in members:
            mumber_dict = {}
            mumber_dict['g_mumber_name'] = mumber['NickName']
            mumber_dict['g_mumber_id'] = mumber['UserName']
            group_mumbers.append(mumber_dict)
        group_dict['group_mumbers'] = group_mumbers
        groups.append(group_dict)
    #print(groups)
    print('-----目前存在的群如下：------')
    i = 0
    num_list = []
    for group in groups:
        i = i+1
        print('%s: %s' % (i, group['group_name']))
        num_list.append(i)

    gsend_num = int(input('请选择发送消息的群号：'))
    if gsend_num not in num_list:
        print('请输入正确的群号！')
        return {'status': 'error'}

    send_group = groups[int(gsend_num)-1]
    send_group_id = send_group['group_id']
    send_group_name = send_group['group_name']
    print('-----%s 群里面有如下群成员：------' % send_group['group_name'])
    i = 0
    num_list = []
    for mumber in send_group['group_mumbers']:
        i = i + 1
        print('%s: %s' % (i, mumber['g_mumber_name']))
        num_list.append(i)
    mumber_num = int(input('请选择发送消息的群成员号：'))
    if mumber_num in num_list:
        send_member = send_group['group_mumbers'][int(mumber_num)-1]
        send_user_id = send_member['g_mumber_id']
        send_user_name = send_member['g_mumber_name']
    elif mumber_num == 0:
        send_user_id = ''
        send_user_name = ''
    else:
        print('请输入正确的群成员号！')
        return {'status': 'error'}
    print('-----目前存在的群如下：------')
    i = 0
    num_list = []
    for group in groups:
        i = i + 1
        if group['group_id'] == send_group_id:
            continue
        print('%s: %s' % (i, group['group_name']))
        num_list.append(i)
    gresev_nums = input('请选择要接收消息的群号, 用空格分割群号：').split( )
    for gresev_num in gresev_nums:
        if int(gresev_num) not in num_list:
            print('请输入正确的群号！')
            return {'status': 'error'}
    resev_groups = [groups[int(gresev_num)-1] for gresev_num in gresev_nums]
    # rsev_group_id = resev_group['group_id']
    # rsev_group_name = resev_group['group_name']
    if not send_user_id:
        print('我们将接收 %s 群里面, 所有成员的消息, 转发到:' % send_group_name)
    else:
        print('我们将接收 %s 群里面, %s 成员的消息, 转发到:' % (send_group_name, send_user_name))
    for resev_group in resev_groups:
        print('%s 群' % resev_group['group_name'])
    return {'status': 'success', 'result': {'send_user_id': send_user_id, 'send_group_id': send_group_id, 'resev_groups': resev_groups}}


if __name__ == "__main__":
    info = login()
    if info['status'] == 'success':
        SEND_USER_ID = info['result']['send_user_id']
        SEND_GROUP_ID = info['result']['send_group_id']
        RESEV_GROUPS = info['result']['resev_groups']
        itchat.run()
