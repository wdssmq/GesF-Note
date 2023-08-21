import { SITE_TITLE, SITE_DESCRIPTION } from "../consts";

const today = new Date();
const copy = `©${today.getFullYear()} 沉冰浮水`;

export const config = {
    site: {
        url: "/",
        title: SITE_TITLE,
        description: SITE_DESCRIPTION,
        favicon: "/favicon.ico",
        image: "/placeholder-hero.jpg",
        copy: copy,
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
