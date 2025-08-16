#!/bin/bash

# Security Verification Script for Plato System
# This script verifies that all security measures are in place

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔒 Plato Security Verification Script${NC}"
echo "========================================"
echo ""

# Track overall security status
SECURITY_STATUS="PASS"

# 1. Check dangerous mock server is removed
echo -e "${YELLOW}1. Checking for dangerous mock server...${NC}"
if [ -f "minimal_plato_server.py" ]; then
    echo -e "${RED}❌ CRITICAL: Dangerous mock server still exists!${NC}"
    echo "   This file contains harmful mock implementations that will hurt humans!"
    echo "   Run: mv minimal_plato_server.py minimal_plato_server.py.DANGEROUS_BACKUP"
    SECURITY_STATUS="FAIL"
else
    echo -e "${GREEN}✅ Dangerous mock server has been removed${NC}"
fi

# 2. Verify backup exists for forensics
echo -e "${YELLOW}2. Checking for forensic backup...${NC}"
if [ -f "minimal_plato_server.py.DANGEROUS_MOCK_BACKUP" ]; then
    echo -e "${GREEN}✅ Backup exists for forensic analysis${NC}"
else
    echo -e "${YELLOW}⚠️  No backup found (may have been permanently deleted)${NC}"
fi

# 3. Check no references to dangerous server
echo -e "${YELLOW}3. Checking for references to dangerous server...${NC}"
REFERENCES=$(grep -r "minimal_plato_server" . --exclude-dir=venv --exclude-dir=htmlcov --exclude-dir=dist --exclude-dir=build --exclude="*.md" --exclude="verify_security.sh" 2>/dev/null | wc -l)
if [ "$REFERENCES" -eq 0 ]; then
    echo -e "${GREEN}✅ No references to dangerous server found${NC}"
else
    echo -e "${RED}❌ Found $REFERENCES references to dangerous server!${NC}"
    grep -r "minimal_plato_server" . --exclude-dir=venv --exclude-dir=htmlcov --exclude-dir=dist --exclude-dir=build --exclude="*.md" --exclude="verify_security.sh" 2>/dev/null | head -5
    SECURITY_STATUS="FAIL"
fi

# 4. Verify real server exists
echo -e "${YELLOW}4. Checking for real server implementation...${NC}"
if [ -f "plato/server/api.py" ]; then
    echo -e "${GREEN}✅ Real server implementation exists${NC}"
    
    # Check for security imports
    if grep -q "from ..core.security import" plato/server/api.py; then
        echo -e "${GREEN}   ✅ Security module imported${NC}"
    else
        echo -e "${RED}   ❌ Security module not imported!${NC}"
        SECURITY_STATUS="FAIL"
    fi
else
    echo -e "${RED}❌ Real server implementation missing!${NC}"
    SECURITY_STATUS="FAIL"
fi

# 5. Verify security module exists
echo -e "${YELLOW}5. Checking security module...${NC}"
if [ -f "plato/core/security.py" ]; then
    echo -e "${GREEN}✅ Security module exists${NC}"
    
    # Check for key security features
    FEATURES_FOUND=0
    
    if grep -q "class APIKeyValidator" plato/core/security.py; then
        echo -e "${GREEN}   ✅ API key validation implemented${NC}"
        ((FEATURES_FOUND++))
    fi
    
    if grep -q "class RateLimitMiddleware" plato/core/security.py; then
        echo -e "${GREEN}   ✅ Rate limiting implemented${NC}"
        ((FEATURES_FOUND++))
    fi
    
    if grep -q "class SecurityHeadersMiddleware" plato/core/security.py; then
        echo -e "${GREEN}   ✅ Security headers implemented${NC}"
        ((FEATURES_FOUND++))
    fi
    
    if grep -q "CSP_POLICY" plato/core/security.py; then
        echo -e "${GREEN}   ✅ Content Security Policy configured${NC}"
        ((FEATURES_FOUND++))
    fi
    
    if [ "$FEATURES_FOUND" -lt 4 ]; then
        echo -e "${YELLOW}   ⚠️  Only $FEATURES_FOUND/4 security features found${NC}"
    fi
else
    echo -e "${RED}❌ Security module missing!${NC}"
    SECURITY_STATUS="FAIL"
fi

# 6. Check startup script
echo -e "${YELLOW}6. Checking startup script...${NC}"
if [ -f "start_plato.sh" ]; then
    if grep -q "python -m plato.server.api" start_plato.sh; then
        echo -e "${GREEN}✅ Startup script uses real server${NC}"
    else
        echo -e "${RED}❌ Startup script doesn't use real server!${NC}"
        SECURITY_STATUS="FAIL"
    fi
else
    echo -e "${YELLOW}⚠️  No startup script found${NC}"
fi

# 7. Check for wildcard CORS in any Python files
echo -e "${YELLOW}7. Checking for dangerous CORS configurations...${NC}"
WILDCARD_CORS=$(grep -r 'allow_origins=\["*"\]' . --include="*.py" --exclude-dir=venv 2>/dev/null | wc -l)
if [ "$WILDCARD_CORS" -eq 0 ]; then
    echo -e "${GREEN}✅ No wildcard CORS configurations found${NC}"
else
    echo -e "${RED}❌ Found $WILDCARD_CORS wildcard CORS configurations!${NC}"
    grep -r 'allow_origins=\["*"\]' . --include="*.py" --exclude-dir=venv 2>/dev/null | head -3
    SECURITY_STATUS="FAIL"
fi

# 8. Check for environment configuration
echo -e "${YELLOW}8. Checking environment configuration...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Environment file exists${NC}"
    
    # Check for security-related environment variables
    if grep -q "PLATO_REQUIRE_API_KEY" .env 2>/dev/null; then
        echo -e "${GREEN}   ✅ API key requirement configured${NC}"
    else
        echo -e "${YELLOW}   ⚠️  API key requirement not configured${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No .env file found (using defaults)${NC}"
fi

# 9. Check for sensitive data in logs
echo -e "${YELLOW}9. Checking for sensitive data exposure...${NC}"
if [ -f "plato_server.log" ]; then
    SENSITIVE_PATTERNS=("password" "api_key" "secret" "token" "bearer")
    SENSITIVE_FOUND=0
    
    for pattern in "${SENSITIVE_PATTERNS[@]}"; do
        if grep -qi "$pattern" plato_server.log 2>/dev/null; then
            ((SENSITIVE_FOUND++))
        fi
    done
    
    if [ "$SENSITIVE_FOUND" -eq 0 ]; then
        echo -e "${GREEN}✅ No obvious sensitive data in logs${NC}"
    else
        echo -e "${YELLOW}⚠️  Potential sensitive data found in logs ($SENSITIVE_FOUND patterns)${NC}"
        echo "   Review logs and implement data masking"
    fi
else
    echo -e "${GREEN}✅ No log file present${NC}"
fi

# 10. Check Python dependencies for known vulnerabilities
echo -e "${YELLOW}10. Checking Python dependencies...${NC}"
if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✅ Dependency files found${NC}"
    echo -e "${YELLOW}   Run 'pip-audit' to check for vulnerabilities${NC}"
else
    echo -e "${YELLOW}⚠️  No dependency files found${NC}"
fi

echo ""
echo "========================================"

# Final verdict
if [ "$SECURITY_STATUS" = "PASS" ]; then
    echo -e "${GREEN}🎉 SECURITY VERIFICATION PASSED${NC}"
    echo -e "${GREEN}The dangerous mock server has been eliminated and${NC}"
    echo -e "${GREEN}proper security measures are in place.${NC}"
else
    echo -e "${RED}🚨 SECURITY VERIFICATION FAILED${NC}"
    echo -e "${RED}Critical security issues detected!${NC}"
    echo -e "${RED}Human safety is at risk until these are fixed!${NC}"
fi

echo ""
echo -e "${BLUE}Recommendations:${NC}"
echo "1. Enable API key requirement in production"
echo "2. Configure proper CORS origins for your domain"
echo "3. Enable HTTPS with valid certificates"
echo "4. Implement regular security audits"
echo "5. Monitor logs for suspicious activity"
echo "6. Keep dependencies updated with 'pip-audit'"
echo ""

exit $([ "$SECURITY_STATUS" = "PASS" ] && echo 0 || echo 1)