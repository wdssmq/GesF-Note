// Place any global data in this file.
// You can import this data from anywhere in your site by using the `import` keyword.

import type { UserConfig } from "@/theme-simple/config.d"
// 你可以在这里覆盖默认配置，不需要每项都写，每项的子项也是可选的。
export const usrConfig: UserConfig = {
    site: {
        url: "/",
        title: 'GesF Note',
        description: '咸鱼纪要 - diu 协会活动记录（雾丨GesF Lib',
        favicon: "/favicon.ico",
        image: "/placeholder-hero.jpg",
        copy: "©{curFullYear} 沉冰浮水",
        locales: "zh-CN", // 'en-us'
    },
    author: {
        name: "沉冰浮水",
        avatar: "/avatar.png",
        bio: "置百丈玄冰而崩裂，掷须臾池水而漂摇。",
    },
    menus: [
        { name: '首页', path: '/' },
        { name: '归档', path: '/archive' },
        { name: '关于', path: '/about' },
    ],
    archive: {
        title: "归档",
        description: "归档文章列表",
    },
};
