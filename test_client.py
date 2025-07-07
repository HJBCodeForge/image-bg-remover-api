import requests
import json
import sys
import os

class BGRemoverAPIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_key = None
    
    def create_api_key(self, name):
        """Create a new API key"""
        url = f"{self.base_url}/api-keys"
        payload = {"name": name}
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            self.api_key = data["key"]
            
            print(f"✅ API Key created successfully!")
            print(f"🔑 API Key: {self.api_key}")
            print(f"📝 Name: {data['name']}")
            print(f"🆔 ID: {data['id']}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating API key: {e}")
            return None
    
    def remove_background(self, image_path, output_path=None, return_json=False):
        """Remove background from an image"""
        if not self.api_key:
            print("❌ No API key set. Please create one first.")
            return None
        
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return None
        
        url = f"{self.base_url}/remove-background"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        # Prepare files and data
        with open(image_path, 'rb') as f:
            files = {"file": f}
            data = {"return_json": str(return_json).lower()}
            
            try:
                print(f"🖼️  Processing image: {image_path}")
                response = requests.post(url, files=files, data=data, headers=headers)
                response.raise_for_status()
                
                if return_json:
                    # JSON response
                    result = response.json()
                    print(f"✅ Processing completed in {result['processing_time']:.2f} seconds")
                    return result
                else:
                    # Binary image response
                    if output_path is None:
                        filename = os.path.basename(image_path)
                        name, ext = os.path.splitext(filename)
                        output_path = f"{name}_no_bg.png"
                    
                    with open(output_path, 'wb') as output_file:
                        output_file.write(response.content)
                    
                    processing_time = response.headers.get('X-Processing-Time', 'N/A')
                    print(f"✅ Background removed successfully!")
                    print(f"⏱️  Processing time: {processing_time}s")
                    print(f"💾 Saved to: {output_path}")
                    
                    return {"output_path": output_path, "processing_time": processing_time}
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Error processing image: {e}")
                return None
    
    def list_api_keys(self):
        """List all API keys"""
        url = f"{self.base_url}/api-keys"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            api_keys = response.json()
            
            print(f"📋 Found {len(api_keys)} API key(s):")
            print("-" * 80)
            
            for key in api_keys:
                status = "🟢 Active" if key['is_active'] else "🔴 Inactive"
                last_used = key['last_used'] if key['last_used'] else "Never"
                
                print(f"🆔 ID: {key['id']}")
                print(f"📝 Name: {key['name']}")
                print(f"🔑 Key: {key['key'][:20]}...")
                print(f"📊 Usage: {key['usage_count']} times")
                print(f"🕐 Last used: {last_used}")
                print(f"📈 Status: {status}")
                print("-" * 80)
            
            return api_keys
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching API keys: {e}")
            return None

def main():
    print("🎨 Background Remover API - Test Client")
    print("=" * 50)
    
    client = BGRemoverAPIClient()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_client.py create_key <name>")
        print("  python test_client.py remove_bg <image_path> [api_key] [output_path]")
        print("  python test_client.py list_keys")
        print("")
        print("Examples:")
        print("  python test_client.py create_key 'My Test App'")
        print("  python test_client.py remove_bg image.jpg bgr_abc123... output.png")
        print("  python test_client.py list_keys")
        return
    
    command = sys.argv[1]
    
    if command == "create_key":
        if len(sys.argv) < 3:
            print("❌ Please provide a name for the API key")
            return
        
        name = sys.argv[2]
        client.create_api_key(name)
    
    elif command == "remove_bg":
        if len(sys.argv) < 3:
            print("❌ Please provide an image path")
            return
        
        image_path = sys.argv[2]
        
        if len(sys.argv) >= 4:
            client.api_key = sys.argv[3]
        else:
            api_key = input("🔑 Enter your API key: ").strip()
            client.api_key = api_key
        
        output_path = sys.argv[4] if len(sys.argv) >= 5 else None
        
        client.remove_background(image_path, output_path)
    
    elif command == "list_keys":
        client.list_api_keys()
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
