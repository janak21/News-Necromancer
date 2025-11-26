#!/usr/bin/env python3
"""
Comprehensive verification that the codebase is ready for Vercel deployment.
Checks all serverless endpoints, configurations, and dependencies.
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(path, description):
    """Check if a file exists"""
    if os.path.exists(path):
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description} MISSING: {path}")
        return False

def check_handler_format(file_path):
    """Check if a Python file uses BaseHTTPRequestHandler"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            if 'class handler(BaseHTTPRequestHandler)' in content:
                return True
            elif 'handler = Mangum' in content:
                return 'mangum'
            else:
                return False
    except Exception as e:
        print(f"   Error reading {file_path}: {e}")
        return False

def main():
    print("=" * 70)
    print("Vercel Deployment Readiness Check")
    print("=" * 70)
    print()
    
    all_checks_passed = True
    
    # 1. Check Vercel configuration
    print("📋 1. Vercel Configuration")
    print("-" * 70)
    if check_file_exists("vercel.json", "Vercel config"):
        with open("vercel.json", 'r') as f:
            config = json.load(f)
            print(f"   Build command: {config.get('buildCommand')}")
            print(f"   Output directory: {config.get('outputDirectory')}")
            print(f"   Install command: {config.get('installCommand')}")
    else:
        all_checks_passed = False
    print()
    
    # 2. Check API endpoints
    print("🔌 2. Serverless API Endpoints")
    print("-" * 70)
    
    endpoints = [
        ("api/feeds/process.py", "Feed processing"),
        ("api/narration/generate.py", "Narration generation"),
        ("api/narration/status.py", "Narration status"),
        ("api/story_continue.py", "Story continuation"),
        ("api/health.py", "Health check"),
    ]
    
    for file_path, description in endpoints:
        if os.path.exists(file_path):
            handler_type = check_handler_format(file_path)
            if handler_type is True:
                print(f"✅ {description}: {file_path}")
                print(f"   Handler: BaseHTTPRequestHandler ✓")
            elif handler_type == 'mangum':
                print(f"⚠️  {description}: {file_path}")
                print(f"   Handler: Mangum (may not work on Vercel)")
                all_checks_passed = False
            else:
                print(f"❌ {description}: {file_path}")
                print(f"   Handler: Unknown or missing")
                all_checks_passed = False
        else:
            print(f"❌ {description} MISSING: {file_path}")
            all_checks_passed = False
    print()
    
    # 3. Check dependencies
    print("📦 3. Dependencies")
    print("-" * 70)
    if check_file_exists("api/requirements.txt", "API requirements"):
        with open("api/requirements.txt", 'r') as f:
            lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]
            print(f"   Total dependencies: {len(lines)}")
            
            required = ['aiohttp', 'feedparser']
            for req in required:
                if any(req in line for line in lines):
                    print(f"   ✅ {req}")
                else:
                    print(f"   ❌ {req} MISSING")
                    all_checks_passed = False
    else:
        all_checks_passed = False
    print()
    
    # 4. Check frontend configuration
    print("🎨 4. Frontend Configuration")
    print("-" * 70)
    check_file_exists("frontend/.env.production", "Production env")
    check_file_exists("frontend/package.json", "Package.json")
    check_file_exists("frontend/vite.config.ts", "Vite config")
    
    if os.path.exists("frontend/.env.production"):
        with open("frontend/.env.production", 'r') as f:
            content = f.read()
            if 'VITE_API_BASE_URL' in content:
                print("   ✅ VITE_API_BASE_URL configured")
            else:
                print("   ⚠️  VITE_API_BASE_URL not found")
    print()
    
    # 5. Check environment variables documentation
    print("🔑 5. Environment Variables")
    print("-" * 70)
    check_file_exists(".env.production.example", "Production env example")
    
    required_vars = ['OPENROUTER_API_KEY', 'ELEVENLABS_API_KEY']
    if os.path.exists(".env.production.example"):
        with open(".env.production.example", 'r') as f:
            content = f.read()
            for var in required_vars:
                if var in content:
                    print(f"   ✅ {var} documented")
                else:
                    print(f"   ⚠️  {var} not documented")
    print()
    
    # 6. Check for Python keyword issues
    print("🐍 6. Python Compatibility")
    print("-" * 70)
    api_files = list(Path('api').rglob('*.py'))
    keyword_issues = []
    for file_path in api_files:
        if 'continue.py' in str(file_path):
            keyword_issues.append(str(file_path))
    
    if keyword_issues:
        print("   ⚠️  Files with Python keyword names:")
        for issue in keyword_issues:
            print(f"      {issue}")
        print("   Note: 'continue' is a Python keyword and may cause import issues")
    else:
        print("   ✅ No Python keyword conflicts")
    print()
    
    # 7. Summary
    print("=" * 70)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - Ready for Vercel deployment!")
        print()
        print("Next steps:")
        print("1. Ensure environment variables are set in Vercel Dashboard")
        print("2. git push origin main")
        print("3. Vercel will auto-deploy")
        print("4. Test all features on production URL")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Review issues above")
        print()
        print("Fix the issues and run this script again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
