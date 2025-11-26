#!/bin/bash
# Script to set up Vercel environment variables

echo "Setting up Vercel environment variables..."

# Set OPENROUTER_API_KEY
vercel env add OPENROUTER_API_KEY production <<EOF
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
EOF

# Set ELEVENLABS_API_KEY
vercel env add ELEVENLABS_API_KEY production <<EOF
sk_aaf84857f5b144a7f6cc033e3a933f2e1d522f94d8183e78
EOF

# Set OPENROUTER_MODEL (optional)
vercel env add OPENROUTER_MODEL production <<EOF
openai/gpt-3.5-turbo
EOF

echo "✅ Environment variables set!"
echo "Now redeploy your application with: vercel --prod"
