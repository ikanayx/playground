import json
import time
import requests
from typing import List
import os
import gzip
from collections import Counter
from dotenv import load_dotenv

def request_gaode_api(city_name: str, api_url_template: str) -> dict:
    """
    请求高德接口
    """
    try:
        # 拼接完整的接口URL
        url = api_url_template + city_name
        
        # 发送HTTP请求
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 检查HTTP状态码
        
        # 解析JSON响应
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求接口失败 - 城市: {city_name}, 错误: {e}")
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        print(f"JSON解析失败 - 城市: {city_name}, 错误: {e}")
        return {"error": "Invalid JSON response"}

def process_city_name(city_name: str) -> str:
    """
    处理城市名称：如果以"市"结尾，移除末尾的"市"字
    """
    # if city_name.endswith("市"):
    #     return city_name[:-1]
    return city_name

def save_json_response(response_data: dict, city_name: str, output_dir: str):
    """
    将JSON响应保存到本地文件
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 将JSON数据转换为紧凑格式的字节串
        # 使用separators参数去除不必要的空格，实现紧凑压缩
        json_text = json.dumps(response_data, ensure_ascii=False, 
                                separators=(',', ':'), indent=None)
    
        # 构建文件名
        filepath_json = os.path.join(output_dir, f"{city_name}.json")
        if not os.path.exists(filepath_json):
            # 使用紧凑压缩格式保存JSON
            with open(filepath_json, 'w', encoding='utf-8') as f:
                f.write(json_text)
            print(f"已保存: {filepath_json}")
        else:
          print(f"跳过: {filepath_json}")

        filepath_gzip = os.path.join(output_dir, f"{city_name}.json.gz")
        if not os.path.exists(filepath_gzip):
            # 使用gzip压缩字节数据
            compressed_data = gzip.compress(json_text.encode('utf-8'), compresslevel=6)
            # 写入gzip文件
            with open(filepath_gzip, 'wb') as f:
                f.write(compressed_data)
            # 获取压缩后的文件大小
            file_size = os.path.getsize(filepath_gzip)
            original_size = len(json_text)
            compression_ratio = file_size / original_size if original_size > 0 else 0
            print(f"已保存: {filepath_gzip} ({file_size:,} bytes, 压缩率: {compression_ratio:.1%})")
        else:
          print(f"跳过: {filepath_json}")
    except Exception as e:
        print(f"保存文件失败 - 城市: {city_name}, 错误: {e}")

def process_cities_with_rate_limit(city_list: List[str], api_url_template: str, 
                                   output_dir: str, max_per_second: int = 10):
    """
    处理城市列表，限制每秒请求次数
    """
    total_cities = len(city_list)
    processed_count = 0
    
    print(f"开始处理 {total_cities} 个城市...")
    
    # 计算每次请求之间的最小时间间隔（秒）
    min_interval = 1.0 / max_per_second
    
    for i, original_city_name in enumerate(city_list, 1):
        try:
            # 1. 处理城市名称
            processed_city_name = process_city_name(original_city_name)
            
            # 记录开始时间
            start_time = time.time()
            
            # 2. 请求高德接口
            print(f"[{i}/{total_cities}] 处理中: {original_city_name} -> {processed_city_name}")
            response_data = request_gaode_api(processed_city_name, api_url_template)
            
            # 3. 保存响应到本地
            save_json_response(response_data, original_city_name, output_dir)
            
            processed_count += 1
            
            # 4. 控制请求频率
            elapsed_time = time.time() - start_time
            
            # 如果处理时间小于最小间隔，则等待剩余时间
            if elapsed_time < min_interval:
                wait_time = min_interval - elapsed_time
                time.sleep(wait_time)
                
        except Exception as e:
            print(f"处理城市失败: {original_city_name}, 错误: {e}")
            continue
    
    print(f"处理完成！成功处理 {processed_count}/{total_cities} 个城市")
    print(f"文件保存在: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    load_dotenv()

    amap_js_key = os.getenv("AMAP_JS_KEY")
    amap_js_code = os.getenv("AMAP_SECURITY_JS_CODE")

    # 城市列表（示例，可以根据需要扩展）
    # cityList = ["北京市"]
    cityList = ["北京市","天津市","石家庄市","唐山市","秦皇岛市","邯郸市","邢台市","保定市","张家口市","承德市","沧州市","廊坊市","衡水市","太原市","大同市","阳泉市","长治市","晋城市","朔州市","晋中市","运城市","忻州市","临汾市","吕梁市","呼和浩特市","包头市","乌海市","赤峰市","通辽市","鄂尔多斯市","呼伦贝尔市","巴彦淖尔市","乌兰察布市","兴安盟","锡林郭勒盟","阿拉善盟","沈阳市","大连市","鞍山市","抚顺市","本溪市","丹东市","锦州市","营口市","阜新市","辽阳市","盘锦市","铁岭市","朝阳市","葫芦岛市","长春市","吉林市","四平市","辽源市","通化市","白山市","松原市","白城市","延边朝鲜族自治州","哈尔滨市","齐齐哈尔市","鸡西市","鹤岗市","双鸭山市","大庆市","伊春市","佳木斯市","七台河市","牡丹江市","黑河市","绥化市","大兴安岭地区","上海市","南京市","无锡市","徐州市","常州市","苏州市","南通市","连云港市","淮安市","盐城市","扬州市","镇江市","泰州市","宿迁市","杭州市","宁波市","温州市","嘉兴市","湖州市","绍兴市","金华市","衢州市","舟山市","台州市","丽水市","合肥市","芜湖市","蚌埠市","淮南市","马鞍山市","淮北市","铜陵市","安庆市","黄山市","滁州市","阜阳市","宿州市","六安市","亳州市","池州市","宣城市","福州市","厦门市","莆田市","三明市","泉州市","漳州市","南平市","龙岩市","宁德市","南昌市","景德镇市","萍乡市","九江市","新余市","鹰潭市","赣州市","吉安市","宜春市","抚州市","上饶市","济南市","青岛市","淄博市","枣庄市","东营市","烟台市","潍坊市","济宁市","泰安市","威海市","日照市","临沂市","德州市","聊城市","滨州市","菏泽市","郑州市","开封市","洛阳市","平顶山市","安阳市","鹤壁市","新乡市","焦作市","濮阳市","许昌市","漯河市","三门峡市","南阳市","商丘市","信阳市","周口市","驻马店市","省直辖县","武汉市","黄石市","十堰市","宜昌市","襄阳市","鄂州市","荆门市","孝感市","荆州市","黄冈市","咸宁市","随州市","恩施土家族苗族自治州","省直辖县","长沙市","株洲市","湘潭市","衡阳市","邵阳市","岳阳市","常德市","张家界市","益阳市","郴州市","永州市","怀化市","娄底市","湘西土家族苗族自治州","广州市","韶关市","深圳市","珠海市","汕头市","佛山市","江门市","湛江市","茂名市","肇庆市","惠州市","梅州市","汕尾市","河源市","阳江市","清远市","东莞市","中山市","潮州市","揭阳市","云浮市","南宁市","柳州市","桂林市","梧州市","北海市","防城港市","钦州市","贵港市","玉林市","百色市","贺州市","河池市","来宾市","崇左市","海口市","三亚市","三沙市","儋州市","省直辖县","重庆市","县","成都市","自贡市","攀枝花市","泸州市","德阳市","绵阳市","广元市","遂宁市","内江市","乐山市","南充市","眉山市","宜宾市","广安市","达州市","雅安市","巴中市","资阳市","阿坝藏族羌族自治州","甘孜藏族自治州","凉山彝族自治州","贵阳市","六盘水市","遵义市","安顺市","毕节市","铜仁市","黔西南布依族苗族自治州","黔东南苗族侗族自治州","黔南布依族苗族自治州","昆明市","曲靖市","玉溪市","保山市","昭通市","丽江市","普洱市","临沧市","楚雄彝族自治州","红河哈尼族彝族自治州","文山壮族苗族自治州","西双版纳傣族自治州","大理白族自治州","德宏傣族景颇族自治州","怒江傈僳族自治州","迪庆藏族自治州","拉萨市","日喀则市","昌都市","林芝市","山南市","那曲市","阿里地区","西安市","铜川市","宝鸡市","咸阳市","渭南市","延安市","汉中市","榆林市","安康市","商洛市","兰州市","嘉峪关市","金昌市","白银市","天水市","武威市","张掖市","平凉市","酒泉市","庆阳市","定西市","陇南市","临夏回族自治州","甘南藏族自治州","西宁市","海东市","海北藏族自治州","黄南藏族自治州","海南藏族自治州","果洛藏族自治州","玉树藏族自治州","海西蒙古族藏族自治州","银川市","石嘴山市","吴忠市","固原市","中卫市","乌鲁木齐市","克拉玛依市","吐鲁番市","哈密市","昌吉回族自治州","博尔塔拉蒙古自治州","巴音郭楞蒙古自治州","阿克苏地区","克孜勒苏柯尔克孜自治州","喀什地区","和田地区","伊犁哈萨克自治州","塔城地区","阿勒泰地区","自治区直辖县级行政区划","台北市","高雄市","台南市","台中市","金门县","南投县","基隆市","新竹市","嘉义市","新北市","宜兰县","新竹县","桃园市","苗栗县","彰化县","嘉义县","云林县","屏东县","台东县","花莲县","澎湖县","连江县","香港岛","九龙","新界","澳门半岛","离岛"]
    
    # 手动指定的高德接口地址模板
    # 注意：这里使用示例URL，实际使用时需要替换为真实的高德API地址和参数
    api_url_template = f"https://restapi.amap.com/v3/config/district?platform=JS&s=rsv3&logversion=2.0&key={amap_js_key}&sdkversion=2.0.6.4&appname=http%253A%252F%252Flocalhost%253A5173%252Fmap%252Famap-district&csid=1BB81942-EE6A-4084-9BB6-4A86639E811C&jscode={amap_js_code}&subdistrict=0&extensions=all&level=city&showbiz=false&key={amap_js_key}&s=rsv3&keywords="
    
    # 指定本地保存目录
    output_directory = "./city_district"
    
    # 开始处理
    # process_cities_with_rate_limit(cityList, api_url_template, output_directory, 2)
    counter = Counter(cityList)
    duplicates = [item for item, count in counter.items() if count > 1]
    for target in duplicates:
        print(f"重复: {target}")

