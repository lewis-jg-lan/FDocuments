#pragma once

/***************************************************************
* Purpose:   Redis��װ��
* Author:    wuzx ()
* Created:   2016-08-28
**************************************************************/

#include <hiredis.h>
#include <string>
#include <vector>
#include <map>

class CRedis
{
public:

	CRedis();
	~CRedis();

	//���ӷ�����  ����ֵ 0��success; other:failed.
	int Connect(const char* szIp, const int port);

	//�˳�����  ����ֵ 0��success; other:failed.
	int Quit();

	//�ж��Ƿ����ָ����  ����ֵ 0��success; other:failed.
	int IsExistKey(const char* szKey);

	//��ȡlist�ĳ���
	long long GetListLen(const char* szKey);

	//��list�л�ȡһ��Ԫ�� ����ֵ 0��success; other:failed.
	int GetListElement(const char* szKey, long long index, std::string& value);

	//��ȡ�б�����Ԫ�� ����ֵ 0��success; other:failed.
	int GetListAllElement(const char* szKey, std::vector<std::string>& items);

	//�ж�hash��ֵ�Ƿ���� ����ֵ 0��success; other:failed.
	int IsHashKeyExist(const char* szKey, const char* szField);

	//��ȡhashָ��field��ֵ
	int GetHashElement(const char* szKey, const char* szField, std::string& value);

	const char* GetErrMsg(void) const //��ȡ���Ĵ�����Ϣ
	{
		return _szErrMsg;
	}

private:
	redisReply* ExecCommand(const char* szCommand, bool& ret);

private:
	redisContext* _redisCtx;
	char _szErrMsg[1024];
};
