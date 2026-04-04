#include "pid.h"
//#include "common.h"
/**
***********************************************************************
* @brief:      pid_para_init()
* @param[in]:	 pid_config  ָ��pid_para_t�ṹ���ָ��
* @param[in]:	 kp  ��������
* @param[in]:	 ki  ��������
* @param[in]:	 kd  ΢������
* @retval:     void
* @details:    ��ʼ��PID���������� 
***********************************************************************
**/
void pid_para_init(pid_para_t *pid_config)
{
	pid_config->kp = 0.0f;
	pid_config->ki = 0.0f;
	pid_config->kd = 0.0f;

	pid_config->p_term = 0.0f;
	pid_config->i_term = 0.0f;
	pid_config->d_term = 0.0f;
	pid_config->ref_value = 0.0f;
	pid_config->fback_value = 0.0f;
	pid_config->error = 0.0f;
	pid_config->pre_err = 0.0f;
	pid_config->out_value = 0.0f;	
}
/**
***********************************************************************
* @brief:      pid_limit_init
* @param[in]:	 pid_config  ָ��pid_para_t�ṹ���ָ��
* @param[in]:	 i_term_max  ����������
* @param[in]:	 i_term_min  ����������
* @param[in]:	 out_max  �������
* @param[in]:	 out_min  �������
* @retval:     void
* @details:    ����PID���������������������Ʒ�Χ 
***********************************************************************
**/
void pid_limit_init(pid_para_t *pid_config, float i_term_max, float i_term_min,float out_max, float out_min)
{
	pid_config->i_term_max = i_term_max;
	pid_config->i_term_min = i_term_min;
	pid_config->out_max = out_max;
	pid_config->out_min = out_min;
}
/**
***********************************************************************
* @brief:      pid_clear
* @param[in]:	 pid_clear  ָ��pid_para_t�ṹ���ָ��
* @retval:     void
* @details:    ���PID����������ʷ״̬ 
***********************************************************************
**/
void pid_clear(pid_para_t *pid_clear)
{
	pid_clear->p_term = 0.0f;
	pid_clear->i_term = 0.0f;
	pid_clear->d_term = 0.0f;
	pid_clear->error = 0.0f;
	pid_clear->pre_err = 0.0f;
	pid_clear->out_value = 0.0f;
}
/**
***********************************************************************
* @brief:      pid_reset()
* @param[in]:	 pid_config  ָ��pid_para_t�ṹ���ָ��
* @param[in]:	 kp  ��������
* @param[in]:	 ki  ��������
* @param[in]:	 kd  ΢������
* @retval:     void
* @details:    pid�����������޸� 
***********************************************************************
**/
void pid_reset(pid_para_t *pid_config, float kp, float ki, float kd)
{
	pid_config->kp = kp;
	pid_config->ki = ki;
	pid_config->kd = kd;
}
/**
***********************************************************************
* @brief:     	pid_ctrl
* @param[in]:	pid  ָ��pid_para_t�ṹ���ָ��
* @param[in]:	ref_value  Ŀ��ֵ
* @param[in]:	fback_value  ʵ��ֵ
* @retval:   	float  PI�����������ֵ
* @details:  	ʵ��PI�������ļ����߼� 
***********************************************************************
**/
float parallel_pid_ctrl(pid_para_t *pid, float ref_value, float fdback_value) 
{
	pid->ref_value = ref_value;
	pid->fback_value = fdback_value;
	
	pid->error = pid->ref_value - pid->fback_value;
	
	// ���������
	pid->p_term = pid->kp * pid->error;
	
	// ���������
	pid->i_term += pid->ki * pid->error;

	// ���ƻ����Χ
	if (pid->i_term > pid->i_term_max)
		pid->i_term = pid->i_term_max;
	else if (pid->i_term < pid->i_term_min)
		pid->i_term = pid->i_term_min;
	
	// ����΢����
	pid->d_term = pid->kd * (pid->error - pid->pre_err);
	pid->pre_err = pid->error;
	
	// ��������������P��I��D�
	pid->out_value = pid->p_term + pid->i_term + pid->d_term;
	
	// ���������Χ
	if (pid->out_value > pid->out_max)
		pid->out_value = pid->out_max;
	else if (pid->out_value < pid->out_min)
		pid->out_value = pid->out_min;
	
	return pid->out_value;
}


float serial_pid_ctrl(pid_para_t *pid, float ref_value, float fdback_value)
{
	pid->ref_value = ref_value;
	pid->fback_value = fdback_value;
	
	pid->error = pid->ref_value - pid->fback_value;
	
	pid->p_term = pid->kp * pid->error;
	
	pid->i_term += pid->ki * pid->p_term;
	
	if (pid->i_term > pid->i_term_max)
		pid->i_term = pid->i_term_max;
	else if (pid->i_term < pid->i_term_min)
		pid->i_term = pid->i_term_min;
	
	pid->out_value = pid->p_term + pid->i_term;
	

	if (pid->out_value > pid->out_max)
		pid->out_value = pid->out_max;
	else if (pid->out_value < pid->out_min)
		pid->out_value = pid->out_min;
	
	return pid->out_value;
}



