"""智能简历分析系统 - 主API服务"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os

from pdf_parser import extract_text_from_pdf, clean_text
from ai_extractor import extract_resume_info, match_resume_with_job, extract_job_keywords
from cache_manager import cache_manager

app = Flask(__name__, static_folder='static')
CORS(app)


@app.route('/')
def index():
    """返回前端页面"""
    return send_from_directory(app.static_folder, 'index.html')

# 配置
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    """检查文件类型"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'cache_enabled': cache_manager.enabled
    })


@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    """简历上传与解析接口"""
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'error': '未找到文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '仅支持PDF格式'}), 400
        
        # 读取文件内容
        pdf_content = file.read()
        
        # 检查缓存
        cached_result = cache_manager.get_resume_cache(pdf_content)
        if cached_result:
            return jsonify({
                'success': True,
                'cached': True,
                'data': cached_result
            })
        
        # 解析PDF
        text = extract_text_from_pdf(pdf_content)
        cleaned_text = clean_text(text)
        
        # AI提取信息
        resume_info = extract_resume_info(cleaned_text)
        
        result = {
            'resume_info': resume_info,
            'raw_text': cleaned_text[:500] + '...' if len(cleaned_text) > 500 else cleaned_text
        }
        
        # 缓存结果
        cache_manager.set_resume_cache(pdf_content, result)
        
        return jsonify({
            'success': True,
            'cached': False,
            'data': result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/match-resume', methods=['POST'])
def match_resume():
    """简历与岗位匹配接口"""
    try:
        data = request.get_json()
        
        if not data or 'resume_info' not in data or 'job_requirements' not in data:
            return jsonify({'error': '缺少必要参数'}), 400
        
        resume_info = data['resume_info']
        job_requirements = data['job_requirements']
        
        # 检查缓存
        cached_result = cache_manager.get_match_cache(resume_info, job_requirements)
        if cached_result:
            return jsonify({
                'success': True,
                'cached': True,
                'data': cached_result
            })
        
        # 提取岗位关键词
        job_keywords = extract_job_keywords(job_requirements)
        
        # 匹配评分
        match_result = match_resume_with_job(resume_info, job_requirements)
        
        result = {
            'job_keywords': job_keywords,
            'match_result': match_result
        }
        
        # 缓存结果
        cache_manager.set_match_cache(resume_info, job_requirements, result)
        
        return jsonify({
            'success': True,
            'cached': False,
            'data': result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze-resume', methods=['POST'])
def analyze_resume():
    """一站式简历分析接口（上传+匹配）"""
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'error': '未找到文件'}), 400
        
        file = request.files['file']
        job_requirements = request.form.get('job_requirements', '')
        
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': '文件格式错误'}), 400
        
        # 读取并解析PDF
        pdf_content = file.read()
        
        # 检查简历缓存
        cached_resume = cache_manager.get_resume_cache(pdf_content)
        if cached_resume:
            resume_info = cached_resume['resume_info']
        else:
            text = extract_text_from_pdf(pdf_content)
            cleaned_text = clean_text(text)
            resume_info = extract_resume_info(cleaned_text)
            cache_manager.set_resume_cache(pdf_content, {
                'resume_info': resume_info,
                'raw_text': cleaned_text[:500] + '...' if len(cleaned_text) > 500 else cleaned_text
            })
        
        # 如果提供了岗位需求，进行匹配
        match_data = None
        if job_requirements:
            cached_match = cache_manager.get_match_cache(resume_info, job_requirements)
            if cached_match:
                match_data = cached_match
            else:
                job_keywords = extract_job_keywords(job_requirements)
                match_result = match_resume_with_job(resume_info, job_requirements)
                match_data = {
                    'job_keywords': job_keywords,
                    'match_result': match_result
                }
                cache_manager.set_match_cache(resume_info, job_requirements, match_data)
        
        return jsonify({
            'success': True,
            'data': {
                'resume_info': resume_info,
                'match_data': match_data
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
