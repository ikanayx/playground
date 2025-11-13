from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


def save_slide_node_as_image(slides_url, node_selector, output_path):
    # 初始化Chrome浏览器（无头模式，不显示窗口）
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 无头模式，可选
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")  # 设置窗口大小，避免节点被截断

    # 启动浏览器
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        # 访问Google Slides链接
        driver.get(slides_url)

        # 等待页面加载完成（根据实际页面调整等待条件，例如等待第一个幻灯片加载）
        # 这里以等待"slide-container"容器为例，可根据实际节点调整
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".sketchyViewerContent"))
        )
        # 额外等待几秒，确保动态内容（如SVG）完全渲染
        time.sleep(5)

        # 定位目标节点（根据实际需求修改选择器，例如div或svg的CSS选择器）
        # 示例：假设目标是第一个幻灯片中的svg节点
        # node_selector 可以是 ".punch-viewer-content svg" 或其他具体选择器
        target_node = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, node_selector))
        )

        # 截取节点并保存为图片
        target_node.screenshot(output_path)
        print(f"节点已保存至：{output_path}")

    except Exception as e:
        print(f"操作失败：{str(e)}")
    finally:
        # 关闭浏览器
        driver.quit()


# 示例用法
if __name__ == "__main__":
    # Google Slides分享链接（需确保权限为“任何人可查看”）
    slides_url = "https://docs.google.com/presentation/d/e/2PACX-1vQM62P6-WMrWmtwSjVFrDcarzv9ZBJ4qXedm3p0INV5xrRdxZ06ng_0H7naDhUvwQ/pubembed?start=true&loop=false&delayms=60000&pli=1&slide=id.p39"
    # 目标节点的CSS选择器（需根据实际页面结构调整，例如svg节点）
    # node_selector = ".punch-viewer-content svg"  # 示例：幻灯片内容中的svg
    node_selector = ".punch-viewer-svgpage-svgcontainer svg"  # 示例：幻灯片内容中的svg
    # 输出图片路径
    output_image = "slide_node_42.png"

    save_slide_node_as_image(slides_url, node_selector, output_image)