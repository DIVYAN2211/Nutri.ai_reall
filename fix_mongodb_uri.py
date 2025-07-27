#!/usr/bin/env python3
"""
Fix MongoDB URI encoding issues
"""

import urllib.parse
import os
from dotenv import load_dotenv

def fix_mongodb_uri():
    """Fix MongoDB URI encoding issues"""
    
    load_dotenv()
    mongo_uri = os.getenv('MONGO_URI')
    
    if not mongo_uri:
        print("❌ MONGO_URI not found in .env file")
        return
    
    print("🔍 Current MongoDB URI:")
    print(f"   {mongo_uri}")
    
    # Parse the URI to extract components
    try:
        # Split the URI to get username, password, and host
        if 'mongodb+srv://' in mongo_uri:
            # Remove the protocol
            uri_without_protocol = mongo_uri.replace('mongodb+srv://', '')
            
            # Split at @ to separate credentials from host
            if '@' in uri_without_protocol:
                credentials, host_part = uri_without_protocol.split('@', 1)
                
                # Split credentials to get username and password
                if ':' in credentials:
                    username, password = credentials.split(':', 1)
                    
                    # URL encode the password
                    encoded_password = urllib.parse.quote_plus(password)
                    
                    # Reconstruct the URI
                    fixed_uri = f"mongodb+srv://{username}:{encoded_password}@{host_part}"
                    
                    print("\n🔧 Fixed MongoDB URI (with URL encoding):")
                    print(f"   {fixed_uri}")
                    
                    print("\n📝 Update your .env file with this URI:")
                    print(f"MONGO_URI={fixed_uri}")
                    
                    return fixed_uri
                else:
                    print("❌ Could not parse username and password")
            else:
                print("❌ Could not parse host part")
        else:
            print("❌ Not a valid mongodb+srv:// URI")
            
    except Exception as e:
        print(f"❌ Error parsing URI: {e}")
    
    return None

def test_connection_with_fixed_uri(uri):
    """Test connection with the fixed URI"""
    try:
        from pymongo import MongoClient
        
        print(f"\n🧪 Testing connection with fixed URI...")
        client = MongoClient(uri, serverSelectionTimeoutMS=10000)
        
        # Test the connection
        client.admin.command('ping')
        print("✅ Connection successful with fixed URI!")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection still failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 MongoDB URI Fix Tool")
    print("=" * 50)
    
    fixed_uri = fix_mongodb_uri()
    
    if fixed_uri:
        print("\n" + "=" * 50)
        print("🎯 Next Steps:")
        print("1. Copy the fixed URI above")
        print("2. Update your .env file with the new URI")
        print("3. Make sure Network Access is configured in MongoDB Atlas")
        print("4. Test your app again")
        
        # Test the connection
        test_connection_with_fixed_uri(fixed_uri) 