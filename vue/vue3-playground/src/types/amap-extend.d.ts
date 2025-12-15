// amap-extend.d.ts
declare namespace AMap {
  // DistrictSearch 相关类型
  namespace DistrictSearch {
    interface Options {
      /**
       * 行政区级别
       * country:国家
       * province:省份
       * city:市
       * district:区县
       * street:街道
       */
      level?: string
      /**
       * 是否显示商圈
       */
      showbiz?: boolean
      /**
       * 返回查询结果数量
       */
      pageSize?: number
      /**
       * 显示下级行政区级数
       */
      extensions?: string
      /**
       * 查询子级行政区
       */
      subdistrict?: number
    }

    interface District {
      adcode: string
      name: string
      level: string
      center: LngLat
      boundaries?: LngLat[][]
      districtList?: District[]
    }

    interface SearchResult {
      info: string
      districtList: District[]
    }

    interface EventMap {
      complete: SearchResult
      error: { info: string }
    }
  }

  class DistrictSearch {
    constructor(opts?: DistrictSearch.Options)

    /**
     * 根据关键字查询行政区划信息
     * @param keyword 关键词
     * @param callback 回调函数
     */
    search(
      keyword: string,
      callback?: (status: string, result: DistrictSearch.SearchResult) => void,
    ): void

    /**
     * 根据adcode查询行政区划信息
     * @param adcode 行政区划代码
     * @param callback 回调函数
     */
    search(
      adcode: string | number,
      callback?: (status: string, result: DistrictSearch.SearchResult) => void,
    ): void

    /**
     * 设置行政区划查询的级别
     * @param level 级别
     */
    setLevel(level: string): void

    /**
     * 设置下级行政区级数
     * @param district 级数
     */
    setSubdistrict(district: number): void

    /**
     * 注册事件
     */
    on<K extends keyof DistrictSearch.EventMap>(
      event: K,
      callback: (event: DistrictSearch.EventMap[K]) => void,
    ): void

    /**
     * 移除事件
     */
    off<K extends keyof DistrictSearch.EventMap>(
      event: K,
      callback: (event: DistrictSearch.EventMap[K]) => void,
    ): void
  }
}
