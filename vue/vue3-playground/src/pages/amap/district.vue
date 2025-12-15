<template>
  <div class="page-container">
    <div id="map-container" class="map-container"></div>
    <div class="input-card">
      <label style="color: grey">行政区边界查询</label>
      <div class="input-item">
        <div class="input-item-prepend">
          <span class="input-item-text">名称，多个城市用<strong>英文半角逗号</strong>拼接</span>
        </div>
        <input id="district" type="text" v-model="cityList" />
      </div>
      <input id="draw" type="button" class="btn" value="查询" @click="drawCityBounds" />
    </div>
  </div>
</template>

<script setup lang="ts">
import AMapLoader from '@amap/amap-jsapi-loader'
import { areaList } from '@vant/area-data'
import { onMounted, onUnmounted, ref } from 'vue'
import pako from 'pako'

const amap = ref()

async function initMap(
  initConfig = {
    key: '',
    // 在2021年12月02日以后申请的key需要配合安全密钥一起使用
    // 服务端代理进行转发 - 推荐
    serviceHost: '', // "https://your_domain/_AMapService",
    // 直接明文声明安全密钥 - 不安全
    securityJsCode: '',
  },
  option?: AMap.MapOptions,
): Promise<AMap.Map> {
  if (!initConfig?.key) {
    alert('未配置高德地图Key')
    throw new Error('未配置高德地图Key')
  }
  if (initConfig?.serviceHost) {
    console.debug(`serviceHost=${initConfig.serviceHost}`)
  }
  if (initConfig?.securityJsCode) {
    console.warn(`注意安全密钥泄露 securityJsCode=${initConfig.securityJsCode}`)
  }
  window._AMapSecurityConfig = initConfig

  return AMapLoader.load({
    key: initConfig.key, // 申请高德地图key
    version: '2.0', // 指定地图版本
    // 预加载需要使用的插件
    // 插件的更多加载方式参考 https://lbs.amap.com/api/javascript-api-v2/guide/abc/plugins
    // 更多插件清单参考 https://lbs.amap.com/api/javascript-api-v2/guide/abc/plugins-list
    plugins: [
      'AMap.DistrictSearch', // 行政区查询服务
    ],
  })
    .then((AMap) => {
      const defaultOptions: AMap.MapOptions = {
        zoom: 11, //级别
        center: [116.397428, 39.90923], //中心点坐标
        viewMode: '2D', //使用3D视图
      }
      const map = new AMap.Map('map-container', { ...defaultOptions, ...option })
      map.on('complete', function () {
        console.debug('amap实例加载完成')
      })
      map.on('click', function (evt: { lnglat: AMap.LngLat; pixel: AMap.Pixel; type: string }) {
        console.debug(
          `amap地图被点击,类型:${evt.type},位置:lng=${evt.lnglat.getLng()},lat=${evt.lnglat.getLat()}`,
        )
      })
      amap.value = map
      return map
    })
    .catch((e) => {
      console.error(e)
    })
}

const cityList = ref<string>('')
const districtType = ref('city')
let district: AMap.DistrictSearch | null = null
let polygons: AMap.Polygon[] = []

function createSearcher() {
  //加载行政区划插件
  if (district == null) {
    //实例化DistrictSearch
    const opts = {
      subdistrict: 0, // 获取边界不需要返回下级行政区
      extensions: 'all', // 返回行政区边界坐标组等具体信息
      level: 'city', // 查询行政级别为 市
      showbiz: false, // 是否显示商圈，默认值true 可选为true/false，为了能够精准的定位到街道，特别是在快递、物流、送餐等场景下，强烈建议将此设置为false
    }
    district = new AMap.DistrictSearch(opts)
    // district.on('complete', function (res: any) {
    //   console.log('查找行政区边界成功', res)
    // })
    district.on('error', function (err: any) {
      console.log('查找行政区边界异常', err)
    })
  }
}

const polygonOptions = ref<Partial<AMap.PolygonOptions>>({
  strokeWeight: 1,
  fillOpacity: 0.4,
  fillColor: '#fbf130',
  strokeColor: '#0091ea',
})

async function fetchCdnBoundary(identifier: string): Promise<AMap.Polygon[]> {
  const city_list = areaList.city_list as Record<string, string>
  const city_name_list = Object.values(city_list)
  const full_name = city_name_list.find((name) => name === identifier || name === identifier + '市')
  if (!full_name) {
    return []
  }
  const cdnUrl = `https://path/to/${full_name}.json.gz`
  try {
    const response = await fetch(cdnUrl)
    if (response.status === 404) {
      return []
    }
    const contentType = response.headers.get('content-type') || ''
    let res: any
    if (contentType.includes('gzip')) {
      const arrayBuffer = await response.arrayBuffer()
      const uint8Array = new Uint8Array(arrayBuffer)
      const data = pako.inflate(uint8Array)
      const json_str = new TextDecoder('utf-8').decode(data)
      res = JSON.parse(json_str)
    } else {
      res = await response.json()
    }
    const districts = res.districts as any[]
    return districts.reduce((all, d) => {
      const polyline_str = d.polyline as string
      const polylines = polyline_str.split('|')
      const polygonArr: AMap.Polygon[] = polylines.map((polyline) => {
        const path: AMap.LngLat[] = polyline.split(';').map((lnglat: string) => {
          const yx = lnglat.split(',')
          const lng = parseFloat(yx[0]!)
          const lat = parseFloat(yx[1]!)
          return new AMap.LngLat(lng, lat)
        })
        //生成行政区划polygon
        const polygon = new AMap.Polygon()
        polygon.setOptions({
          ...polygonOptions.value,
          path,
        })
        return polygon
      })
      return all.concat(polygonArr)
    }, [] as AMap.Polygon[])
  } catch (e: any) {
    return []
  }
}

function fetchAMapBoundary(identifier: string): Promise<AMap.Polygon[]> {
  return new Promise((resolve, reject) => {
    if (district == null) {
      return reject('搜索插件未初始化')
    }
    district.search(
      identifier,
      function (
        status: string, // 'complete' | 'error' | 'no_data'
        result: AMap.DistrictSearch.SearchResult,
      ) {
        if (status === 'complete') {
          const polygonArr: AMap.Polygon[] = []
          const bounds = result.districtList?.[0]?.boundaries
          if (bounds) {
            for (let i = 0, l = bounds.length; i < l; i++) {
              //生成行政区划polygon
              const polygon = new AMap.Polygon()
              polygon.setOptions({
                ...polygonOptions.value,
                path: bounds[i],
              })
              polygonArr.push(polygon)
            }
          }
          resolve(polygonArr)
        } else if (status === 'no_data') {
          resolve([])
        } else {
          reject('搜索行政区边界异常:' + result.info)
        }
      },
    )
  })
}

async function drawCityBounds() {
  const map = amap.value
  if (map == null) {
    return Promise.reject('地图未初始化')
  }
  if (district == null) {
    return Promise.reject('搜索插件未初始化')
  }

  // 清除上次结果
  map.remove(polygons)
  polygons = []

  // 行政区查询
  district.setLevel('city')
  const cities = cityList.value.split(',')
  for (const city of cities) {
    const ls = window.localStorage
    const ls_key = `amap_district_boundary_${city}`
    const data = ls.getItem(ls_key)
    if (data) {
      continue
    }
    let polygonArr: AMap.Polygon[]

    // 从cdn获取边界
    polygonArr = await fetchCdnBoundary(city)

    // cdn没有该城市的边界数据
    if (!polygonArr.length) {
      // 使用高德插件获取边界
      polygonArr = await fetchAMapBoundary(city)
      if (polygonArr.length) {
        console.log(`从高德地图插件获得城市"${city}"边界数据`)
      } else {
        console.warn(`无法获得城市"${city}"边界数据`)
      }
    } else {
      console.log(`从CDN获得城市"${city}"边界数据`)
    }

    if (polygonArr.length) {
      polygons = polygons.concat(polygonArr)
    }
  }
  map.add(polygons)

  // 视口自适应
  map.setFitView(polygons)
}

onMounted(async () => {
  const mapConfig = {
    key: import.meta.env.VITE_AMAP_KEY,
    serviceHost: '',
    securityJsCode: import.meta.env.VITE_AMAP_SECURITY_JS_CODE,
  }
  const mapOption = {
    // mapStyle: import.meta.env.VITE_AMAP_MAP_STYLE,
    mapStyle: 'amap://styles/dark',
    zooms: [3, 9] as [number, number],
  }
  const map = await initMap(mapConfig, mapOption)

  // 创建国家简易行政区图层
  const distCountry = new AMap.DistrictLayer.Country({
    zIndex: 10, //设置图层层级
    zooms: mapOption.zooms, //设置图层显示范围
    SOC: 'CHN', //设置显示国家
    depth: 2, //设置数据显示层级，0：显示国家面，1：显示省级，当国家为中国时设置depth为2的可以显示市一级
  })

  // 设置行政区图层样式
  distCountry.setStyles({
    'stroke-width': 1, //描边线宽
    'province-stroke': '#999EA4',
    'city-stroke': 'rgba(153, 158, 164, 0.1)',
    'county-stroke': '#ffffff00', // 隐藏区县界
    fill: '#191919',
    // fill: function (data) {
    //   // 设置区域填充颜色，可根据回调信息返回区域信息设置不同填充色
    //   // 回调返回区域信息数据，字段包括 SOC(国家代码)、NAME_ENG(英文名称)、NAME_CHN(中文名称)等
    //   // 国家代码名称说明参考 https://a.amap.com/jsapi_demos/static/demo-center/js/soc-list.json
    //   return "#ffffffe7";
    // },
  })

  // 将简易行政区图层添加到地图
  map.add(distCountry)
  map.setZoom(4)

  map.on('zoomend', function () {
    const currLevel = map.getZoom()
    const surroundType = currLevel < 6.2 ? 'province' : 'city'
    districtType.value = surroundType
    console.log(`当前缩放级别:${currLevel}`)
  })
  createSearcher()
})

function destroyMap() {
  console.debug('amap实例销毁')
  amap.value?.destroy()
  amap.value = null
}

onUnmounted(() => {
  destroyMap()
})
</script>

<style scoped>
.page-container {
  background-color: #fff;
}

.map-container {
  width: 100%;
  height: 80vh;
  position: relative;
}
</style>
