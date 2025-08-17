import streamlit as st
import requests
from PIL import Image
import io
import base64
import json
import time

# Set page config
st.set_page_config(
    page_title="🎨 AI Image Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fixed CSS styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .main-header h1 {
        font-size: 3rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-weight: bold;
    }
    .main-header p {
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .example-btn {
        margin: 0.2rem 0;
        padding: 0.3rem 0.6rem;
        background: #f0f2f6;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .example-btn:hover {
        background: #e6e9ef;
        border-color: #667eea;
    }
    .footer {
        text-align: center;
        color: #666;
        padding: 1rem;
        margin-top: 2rem;
        border-top: 1px solid #eee;
        background: #f9f9f9;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

class APIImageGenerator:
    def __init__(self):
        # Multiple free API options
        self.apis = {
            "pollinations": {
                "name": "Pollinations AI",
                "url": "https://image.pollinations.ai/prompt/",
                "type": "direct"
            },
            "huggingface": {
                "name": "Hugging Face (Free)",
                "url": "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
                "type": "post",
                "headers": {}  # No API key needed for free tier
            }
        }
        
        self.style_enhancers = {
            "realistic": "photorealistic, highly detailed, 8k, professional photography",
            "artistic": "artistic, beautiful, masterpiece, oil painting",
            "digital_art": "digital art, concept art, trending on artstation, detailed",
            "anime": "anime style, manga style, cel shading, vibrant colors",
            "vintage": "vintage style, retro, classic, film photography",
            "fantasy": "fantasy art, magical, ethereal, enchanted",
            "cyberpunk": "cyberpunk, neon lights, futuristic, sci-fi",
            "none": ""
        }
    
    def enhance_prompt(self, prompt, style):
        """Enhance prompt with style"""
        enhancer = self.style_enhancers.get(style, "")
        if enhancer:
            return f"{prompt}, {enhancer}, high quality"
        return f"{prompt}, high quality"
    
    def generate_with_pollinations(self, prompt, width=512, height=512):
        """Generate image using Pollinations AI (most reliable free option)"""
        try:
            # Clean prompt for URL
            clean_prompt = prompt.replace(" ", "%20").replace(",", "%2C")
            
            # Build URL
            url = f"{self.apis['pollinations']['url']}{clean_prompt}?width={width}&height={height}&nologo=true&enhance=true"
            
            # Make request
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                # Convert to PIL Image
                image = Image.open(io.BytesIO(response.content))
                return image, "✅ Image generated successfully!"
            else:
                return None, f"❌ API Error: {response.status_code}"
                
        except Exception as e:
            return None, f"❌ Generation failed: {str(e)}"
    
    def generate_with_huggingface(self, prompt):
        """Generate image using Hugging Face Inference API"""
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "num_inference_steps": 20,
                    "guidance_scale": 7.5
                }
            }
            
            response = requests.post(
                self.apis['huggingface']['url'],
                headers=self.apis['huggingface']['headers'],
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                return image, "✅ Image generated successfully!"
            else:
                return None, f"❌ Hugging Face API Error: {response.status_code}"
                
        except Exception as e:
            return None, f"❌ Hugging Face generation failed: {str(e)}"
    
    def generate_image(self, prompt, style="none", width=512, height=512, api_choice="pollinations"):
        """Generate image using selected API"""
        enhanced_prompt = self.enhance_prompt(prompt, style)
        
        if api_choice == "pollinations":
            return self.generate_with_pollinations(enhanced_prompt, width, height)
        elif api_choice == "huggingface":
            return self.generate_with_huggingface(enhanced_prompt)
        else:
            return None, "❌ Invalid API selection"

# Initialize generator
@st.cache_resource
def get_generator():
    return APIImageGenerator()

generator = get_generator()

# Header
st.markdown("""
<div class="main-header">
    <h1>🎨 AI Image Generator</h1>
    <p>Create stunning images with AI-powered APIs - Optimized for Streamlit Cloud</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🎯 Generation Settings")
    
    # API Selection
    st.subheader("🔧 API Provider")
    api_choice = st.selectbox(
        "Choose API:",
        options=["pollinations", "huggingface"],
        format_func=lambda x: {
            "pollinations": "🌟 Pollinations AI (Fast & Reliable)",
            "huggingface": "🤗 Hugging Face (High Quality)"
        }[x],
        help="Pollinations is faster, Hugging Face has better quality"
    )
    
    # Style selection
    style = st.selectbox(
        "🎨 Art Style",
        options=["none", "realistic", "artistic", "digital_art", "anime", "vintage", "fantasy", "cyberpunk"],
        format_func=lambda x: {
            "none": "No Style Enhancement",
            "realistic": "📸 Photorealistic", 
            "artistic": "🎭 Artistic",
            "digital_art": "💻 Digital Art",
            "anime": "🎌 Anime Style",
            "vintage": "📰 Vintage",
            "fantasy": "🧙‍♂️ Fantasy",
            "cyberpunk": "🌆 Cyberpunk"
        }[x]
    )
    
    # Image dimensions
    st.subheader("📏 Image Size")
    if api_choice == "pollinations":
        size_preset = st.selectbox(
            "Size Preset",
            ["512x512 (Square)", "768x512 (Landscape)", "512x768 (Portrait)", "1024x768 (HD Landscape)"]
        )
        
        size_map = {
            "512x512 (Square)": (512, 512),
            "768x512 (Landscape)": (768, 512), 
            "512x768 (Portrait)": (512, 768),
            "1024x768 (HD Landscape)": (1024, 768)
        }
        width, height = size_map[size_preset]
    else:
        st.info("Hugging Face uses default 512x512 size")
        width, height = 512, 512
    
    # API Status
    with st.expander("📊 API Status"):
        st.write("**Pollinations AI**: ✅ No limits, fast")
        st.write("**Hugging Face**: ⚠️ May have rate limits")
        st.write("**Current API**: " + api_choice.title())

# Main interface
col1, col2 = st.columns([3, 2])

with col1:
    st.header("✨ Describe Your Image")
    
    # Prompt input
    prompt = st.text_area(
        "Enter your image description:",
        value="a beautiful sunset over mountains with a calm lake",
        height=100,
        help="Be descriptive! The more details, the better the result."
    )
    
    # Example prompts
    st.subheader("💡 Try These Examples")
    example_prompts = [
        "a majestic dragon flying over a medieval castle",
        "cyberpunk cityscape at night with neon lights", 
        "beautiful fairy in an enchanted forest",
        "steampunk robot in Victorian setting",
        "serene Japanese zen garden with cherry blossoms",
        "abstract cosmic space nebula with bright stars",
        "cozy coffee shop interior with warm lighting",
        "futuristic sports car on a desert highway"
    ]
    
    # Display examples as buttons
    cols = st.columns(2)
    for i, example in enumerate(example_prompts):
        col = cols[i % 2]
        if col.button(f"💡 {example[:35]}...", key=f"example_{i}"):
            st.session_state['selected_prompt'] = example
            st.rerun()
    
    # Update prompt if example was selected
    if 'selected_prompt' in st.session_state:
        prompt = st.session_state['selected_prompt']
        del st.session_state['selected_prompt']
    
    # Generate button
    if st.button("🚀 Generate Image", type="primary"):
        if not prompt.strip():
            st.error("Please enter a description for your image!")
        else:
            with st.spinner(f"🎨 Creating your image using {api_choice.title()}... Please wait..."):
                # Generate image
                image, message = generator.generate_image(
                    prompt=prompt,
                    style=style,
                    width=width,
                    height=height,
                    api_choice=api_choice
                )
                
                if image is not None:
                    st.session_state['generated_image'] = image
                    st.session_state['generation_message'] = message
                    st.session_state['used_prompt'] = generator.enhance_prompt(prompt, style)
                    st.rerun()
                else:
                    st.error(message)
                    # Try fallback API
                    if api_choice == "huggingface":
                        st.info("Trying Pollinations API as fallback...")
                        image, message = generator.generate_image(
                            prompt=prompt,
                            style=style,
                            width=width,
                            height=height,
                            api_choice="pollinations"
                        )
                        if image is not None:
                            st.session_state['generated_image'] = image
                            st.session_state['generation_message'] = "✅ Generated with fallback API!"
                            st.session_state['used_prompt'] = generator.enhance_prompt(prompt, style)
                            st.rerun()

with col2:
    st.header("🖼️ Generated Image")
    
    # Display generated image
    if 'generated_image' in st.session_state:
        st.image(st.session_state['generated_image'], caption="Generated Image", use_column_width=True)
        
        # Success message
        if 'generation_message' in st.session_state:
            st.success(st.session_state['generation_message'])
        
        # Show enhanced prompt
        if 'used_prompt' in st.session_state:
            with st.expander("🔍 Enhanced Prompt Used"):
                st.text(st.session_state['used_prompt'])
        
        # Download button - Fixed implementation
        img_buffer = io.BytesIO()
        st.session_state['generated_image'].save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        st.download_button(
            label="💾 Download Image",
            data=img_bytes,
            file_name="ai_generated_image.png",
            mime="image/png"
        )
        
        # Clear button
        if st.button("🗑️ Clear Image"):
            for key in ['generated_image', 'generation_message', 'used_prompt']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    else:
        st.info("🎯 Enter a prompt and click 'Generate Image' to create your artwork!")
        st.markdown("""
        ### 🌟 Features:
        - **Free APIs** - No API keys required
        - **Multiple styles** - Choose your artistic preference  
        - **Fast generation** - Results in 10-30 seconds
        - **High resolution** - Up to 1024x768 available
        - **Streamlit Cloud optimized** - No memory issues
        """)

# Tips section
with st.expander("💡 Tips for Better Results"):
    st.markdown("""
    **🎯 Prompt Writing Tips:**
    - **Be specific**: Instead of "a dog", try "a golden retriever sitting in a sunny park"
    - **Include details**: Mention colors, lighting, mood, and composition
    - **Use quality terms**: "highly detailed", "beautiful", "masterpiece", "8k"
    - **Specify the medium**: "oil painting", "digital art", "photograph", "sketch"
    - **Add atmosphere**: "dramatic lighting", "soft shadows", "golden hour"
    
    **⚡ Performance Tips:**
    - **Pollinations** is fastest and most reliable
    - **Hugging Face** may be slower but higher quality
    - Use specific style enhancements for better results
    - Try different APIs if one fails
    
    **🎨 Style Guide:**
    - **Realistic**: For photo-like images
    - **Artistic**: For painting-like results
    - **Digital Art**: Modern, concept art style
    - **Anime**: Japanese animation style
    - **Fantasy**: Magical, ethereal themes
    """)

# Performance metrics
if 'generated_image' in st.session_state:
    with st.expander("📊 Generation Info"):
        st.write(f"**API Used**: {api_choice.title()}")
        st.write(f"**Image Size**: {width}x{height}")
        st.write(f"**Style Applied**: {style.title().replace('_', ' ')}")

# Footer
st.markdown("""
<div class="footer">
    🤖 Powered by Free AI APIs | Made with ❤️ using Streamlit<br>
    <small>No API keys required • Optimized for Streamlit Cloud • 100% Free</small>
</div>
""", unsafe_allow_html=True)