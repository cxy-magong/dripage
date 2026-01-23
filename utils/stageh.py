from stagehand import Stagehand, StagehandConfig
from llm.silicon import SiliconModel
from utils.drission_page import create_browser, create_temp_browser
def get_stagehand():
    # browser = create_browser()
    browser = create_temp_browser()
    browser.get("chrome://version")
    
    config = StagehandConfig(
        env="LOCAL",
        headless=False,
        # model_name=f"openai/{SiliconModel.GLM_4_6}",
        model_name=f"openai/{SiliconModel.DEEPSEEK_V3_2}",
        model_api_key=SiliconModel.api_key,
        model_client_options={
            "api_base": SiliconModel.api_url,
        },
        local_browser_launch_options={
            # 'cdp_url': 'http://localhost:19222'
            'cdp_url': browser.browser._ws_address,
        }
    )
    
    print(f"配置的模型: {config.model_name}")
    print(f"API Base: {config.model_client_options.get('api_base')}")
    
    stagehand = Stagehand(config)
    return stagehand
