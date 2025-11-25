"""
Ultra-simple test endpoint without FastAPI.
"""

def handler(event, context):
    """
    Direct Lambda handler without Mangum/FastAPI.
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': '{"status": "success", "message": "Direct handler working!"}'
    }
