export function loadJs(url: string, anonymous = true, callback?: () => void) {
  const script = document.createElement('script')
  const fn = callback || function () {}

  script.type = 'text/javascript'
  if (anonymous) {
    script.crossOrigin = 'anonymous'
  }
  // 现代浏览器使用 onload/onerror 监听加载状态
  script.onload = function () {
    fn() // 加载成功回调
  }
  script.onerror = function () {
    // 加载失败处理
    console.error('脚本加载失败')
  }

  // 如果需要兼容极旧版IE（可选）
  if ((script as any).readyState) {
    ;(script as any).onreadystatechange = function () {
      const readyState = (script as any).readyState
      if (readyState === 'loaded' || readyState === 'complete') {
        ;(script as any).onreadystatechange = null
        fn()
      }
    }
  }

  script.src = url
  document.getElementsByTagName('head')[0]!.appendChild(script)
}

export function loadJsSync(url: string, anonymous = true): Promise<void> {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script')

    script.type = 'text/javascript'
    if (anonymous) {
      script.crossOrigin = 'anonymous'
    }
    // 现代浏览器使用 onload/onerror 监听加载状态
    script.onload = function () {
      resolve() // 加载成功回调
    }
    script.onerror = function (err) {
      // 加载失败处理
      if (err) console.error(err)
      reject(`脚本:${url} 加载失败`)
    }

    // 如果需要兼容极旧版IE（可选）
    if ((script as any).readyState) {
      ;(script as any).onreadystatechange = function () {
        const readyState = (script as any).readyState
        if (readyState === 'loaded' || readyState === 'complete') {
          ;(script as any).onreadystatechange = null
          resolve()
        }
      }
    }

    script.src = url
    document.getElementsByTagName('head')[0]!.appendChild(script)
  })
}
