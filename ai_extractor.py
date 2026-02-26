"""AI信息提取模块 - 使用阿里云通义千问提取简历关键信息"""
import os
import json
import dashscope
from dashscope import Generation

# 配置API Key（从环境变量获取）
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY', '')

EXTRACT_PROMPT = """你是一个专业的简历解析助手。请从以下简历文本中提取关键信息，以JSON格式返回。

简历文本：
{resume_text}

请提取以下信息（如果找不到某项信息，对应字段返回null）：
1. 基本信息：姓名(name)、电话(phone)、邮箱(email)、地址(address)
2. 求职意向(job_intention)
3. 工作年限(work_years)
4. 学历背景(education)
5. 技能列表(skills) - 返回数组格式
6. 工作经历(work_experience) - 返回数组格式，每项包含公司名、职位、时间段、工作内容

请严格按照以下JSON格式返回，不要添加任何其他内容：
{{
    "name": "",
    "phone": "",
    "email": "",
    "address": "",
    "job_intention": "",
    "work_years": "",
    "education": "",
    "skills": [],
    "work_experience": []
}}"""

MATCH_PROMPT = """你是一个专业的招聘助手。请分析以下简历信息与岗位需求的匹配程度。

简历信息：
{resume_info}

岗位需求：
{job_requirements}

请从以下维度进行评分（每项0-100分）并给出分析：
1. 技能匹配度(skill_match)：简历中的技能与岗位要求的匹配程度
2. 经验相关性(experience_relevance)：工作经历与岗位的相关程度
3. 学历匹配度(education_match)：学历是否符合要求
4. 综合评分(overall_score)：综合以上因素的总体评分

请严格按照以下JSON格式返回：
{{
    "skill_match": 0,
    "experience_relevance": 0,
    "education_match": 0,
    "overall_score": 0,
    "matched_skills": [],
    "missing_skills": [],
    "analysis": ""
}}"""


def extract_resume_info(resume_text: str) -> dict:
    """使用AI提取简历关键信息"""
    try:
        response = Generation.call(
            model='qwen-turbo',
            prompt=EXTRACT_PROMPT.format(resume_text=resume_text),
            result_format='message'
        )
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            # 尝试解析JSON
            try:
                # 清理可能的markdown代码块标记
                content = content.strip()
                if content.startswith('```'):
                    content = content.split('\n', 1)[1]
                if content.endswith('```'):
                    content = content.rsplit('```', 1)[0]
                content = content.strip()
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw_response": content, "error": "JSON解析失败"}
        else:
            return {"error": f"API调用失败: {response.message}"}
    except Exception as e:
        return {"error": f"信息提取失败: {str(e)}"}


def match_resume_with_job(resume_info: dict, job_requirements: str) -> dict:
    """将简历与岗位需求进行匹配评分"""
    try:
        response = Generation.call(
            model='qwen-turbo',
            prompt=MATCH_PROMPT.format(
                resume_info=json.dumps(resume_info, ensure_ascii=False, indent=2),
                job_requirements=job_requirements
            ),
            result_format='message'
        )
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            try:
                content = content.strip()
                if content.startswith('```'):
                    content = content.split('\n', 1)[1]
                if content.endswith('```'):
                    content = content.rsplit('```', 1)[0]
                content = content.strip()
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw_response": content, "error": "JSON解析失败"}
        else:
            return {"error": f"API调用失败: {response.message}"}
    except Exception as e:
        return {"error": f"匹配评分失败: {str(e)}"}


def extract_job_keywords(job_requirements: str) -> dict:
    """从岗位需求中提取关键词"""
    prompt = f"""请从以下岗位需求中提取关键信息，以JSON格式返回：

岗位需求：
{job_requirements}

请提取：
1. 必备技能(required_skills) - 数组格式
2. 加分技能(preferred_skills) - 数组格式
3. 学历要求(education_requirement)
4. 经验要求(experience_requirement)
5. 岗位关键词(keywords) - 数组格式

请严格按照JSON格式返回。"""

    try:
        response = Generation.call(
            model='qwen-turbo',
            prompt=prompt,
            result_format='message'
        )
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            try:
                content = content.strip()
                if content.startswith('```'):
                    content = content.split('\n', 1)[1]
                if content.endswith('```'):
                    content = content.rsplit('```', 1)[0]
                content = content.strip()
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw_response": content}
        else:
            return {"error": f"API调用失败: {response.message}"}
    except Exception as e:
        return {"error": f"关键词提取失败: {str(e)}"}
