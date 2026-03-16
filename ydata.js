// 配置数据 - 前端页面渲染所需的所有数据
const CONFIG = {
    // 页面基本配置
    page: {
        title: "命理分析 - 自己"
    },
    
    // 颜色配置
    colors: {
        bgMain: '#FFFFF8',      // 页面主背景（米白色）
        bgCard: '#FDF8F3',      // 卡片背景（稍深的暖米色）
        bgChart: '#FAF5F0',     // 图表区域背景
        textMain: '#5C3D2E',    // 深棕色文字
        // 五行颜色
        fire: '#F8C4C4',        // 浅粉色（火）
        wood: '#C9A66B',        // 浅木色（木）
        water: '#A8D8EA',       // 浅蓝色（水）
        metal: '#F5E6CC',       // 浅金色（金）
        earth: '#D4A574',       // 浅棕色（土）
        // 喜用神颜色
        luckyEarth: '#F5E6CC',  // 浅黄色（土）
        luckyMetal: '#FFFFFF',  // 白色（金）
        // 其他功能色
        halo: 'rgba(248, 196, 196, 0.3)',  // 光晕色
        tagBg: '#F5EDE4'        // 标签背景色
    },
    
    // 导航栏配置
    nav: {
        title: "自己",
        tabs: [
            { name: "沙盘", active: true },
            { name: "星座", active: false },
            { name: "生辰", active: false },
            { name: "星宿", active: false },
            { name: "紫微", active: false }
        ],
        buttons: [
            { icon: "fa-share-alt", text: "分享完整内容" },
            { icon: "fa-calendar", text: "查看生辰历" }
        ]
    },
    
    // 格局配置
    pattern: {
        title: "【这点痛算什么】",
        pattern: "偏财格·损根破格",
        description: "起起伏伏坚韧如你，独自向前的你好似那孤胆英雄，总有一天能突破重围。"
    },
    
    // 五行配置
    fiveElements: {
        title: "【身弱型】",
        chartTitle: "五行占比",
        elements: [
            { label: "火（七杀正官）", percentage: 31, colorClass: "bg-fire" },
            { label: "木（偏财正财）", percentage: 34, colorClass: "bg-wood" },
            { label: "水（食神）", percentage: 3, colorClass: "bg-water" },
            { label: "金（比肩劫财，日主）", percentage: 30, colorClass: "bg-metal" },
            { label: "土（偏印正印）", percentage: 0, colorClass: "bg-earth/50" }
        ],
        chartColors: ['#F8C4C4', '#C9A66B', '#A8D8EA', '#F5E6CC', '#D4A574']
    },
    
    // 喜用神配置
    lucky: {
        title: "【喜用土、金】",
        labels: {
            luckyColor: "幸运颜色",
            luckyDirection: "幸运方向",
            luckyNumber: "幸运数字"
        },
        luckyColors: [
            { name: "黄色", colorClass: "bg-luckyEarth" },
            { name: "白色", colorClass: "bg-luckyMetal" }
        ],
        luckyDirections: ["家乡", "正西"],
        luckyNumbers: ["15", "8"]
    },
    
    // 适配匹配配置
    match: {
        industry: {
            title: "适配行业",
            content: "企事业单位，从事政治、财政、高管类工作"
        },
        partner: {
            title: "匹配伴侣",
            content: "配偶星属木（日主为木/五行能量最高为木）"
        }
    },
    
    // 大运配置
    fortune: {
        title: "大运分析",
        chartTitle: "大运评分",
        periods: [
            { age: "15-24岁", stemBranch: "戊辰", tag: "智慧通达 德才并举", score: 98 },
            { age: "25-34岁", stemBranch: "己巳", tag: "根深叶茂 贵人垂青", score: 89 },
            { age: "35-44岁", stemBranch: "庚午", tag: "福泽绵长 贵人护业", score: 87 },
            { age: "45-54岁", stemBranch: "辛未", tag: "捷足先登 气贯长虹", score: 98 },
            { age: "55-64岁", stemBranch: "壬申", tag: "安守本心 心宽事顺", score: 64 },
            { age: "65-7*岁", stemBranch: "癸*", tag: "收敛 低调", score: 7 }
        ]
    },
    
    // 十神配置
    shishen: {
        title: "十神占比",
        chartTitle: "十神占比",
        labels: ["正官", "七杀", "正财", "偏财", "食神", "伤官", "正印", "偏印", "比肩", "劫财"],
        data: [8, 12, 5, 10, 3, 2, 0, 0, 15, 15],
        colors: ['#F8C4C4', '#E8A0A0', '#C9A66B', '#B89565', '#A8D8EA', '#98C8DA', '#F5E6CC', '#E5D6BC', '#D4A574', '#C49564']
    },
    
    // 神煞配置
    shensha: {
        title: "神煞解析",
        items: [
            { name: "贵人相助", description: "天乙贵人、福星贵人", icon: "fa-star", iconBg: "bg-orange-100", iconColor: "text-orange-500" },
            { name: "慧根发达", description: "太极贵人", icon: "fa-brain", iconBg: "bg-blue-100", iconColor: "text-blue-500" },
            { name: "张力满满", description: "桃花", icon: "fa-heart", iconBg: "bg-yellow-100", iconColor: "text-yellow-500" },
            { name: "天选领导", description: "禄神", icon: "fa-crown", iconBg: "bg-pink-100", iconColor: "text-pink-500" },
            { name: "旷世奇才", description: "学堂", icon: "fa-graduation-cap", iconBg: "bg-sky-100", iconColor: "text-sky-500" }
        ]
    },
    
    // 免责声明
    disclaimer: {
        content: "当前内容为免费内容，仅供您在娱乐中探索自我，不等于专业测评，不代表价值评判，无任何现实指导意义。"
    },
    
    // 底部配置
    footer: {
        title: "日支·正官"
    }
};