
const flowbite = require("flowbite-react/tailwind");
/** @type {import('tailwindcss').Config} */

export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    flowbite.content(),
  ],
  theme: {
    extend: {
      colors: {
        lightPrimaryColor: '#FFFFFF',
        darkPrimaryColor: '#1C1C25',
        lightSecondaryColor: '#F0F8FF',
        darkSecondaryColor: '#12131A',
        lightGrayColor: '#c0c5cb5e',
        darkGrayColor: '#c0c5cb14',
        lightGrayColor2: '#c3cacd66',
        darkGrayColor2: '#c3cacd14',
        lightBlue1: "#D5E6FB",
        darkBlue1: "#062141",
        lightBlue2: "#0060FF",
        darkBlue2: "#1A71FF",
        lightBlue3: "#F2F8FF",
        darkBlue3: "#131313",
        lightBlue4: "#2F80ED",
        lightBlue5: "#2F80ED33",
        darkBlue5: "#4690EF33",
        lightBlue6: "#3380FF",
        darkBlue6: "#4D91FF",
        lightYellow: "#FFEBCD",
        darkYellow: "#493824",
        lightYellow2: "#ff9c0733",
        darkYellow2: "#ff9c0733",
        lightYellow3: "#FFB849",
        darkYellow3: "#FFC163",
        lightPurple: "#DBD3FF",
        darkPurple: "#2A2251",
        lightPurple1: "#4d21ff33",
        darkPurple1: "#623aff33",
        lightPurple2: "#9181DB",
        darkPurple2: "#A294E1",
        lightPink: "#FFD2D2",
        darkPink: "#460000",
        lightPink1: "#F0A0A0",
        darkPink1: "#F0A0A0",
        lightPink2: "#FFD2D2",
        darkPink2: "#460000",
        lightGreen: "#219653",
        darkGreen: "#26AB5F",
        lightGreen1: "#21965333",
        darkGreen1: "#26AB5F33",
        lightGreen2: "#C7E4DB",
        darkGreen2: "#23493D",
        lightRed: "#EB5757",
        darkRed: "#EE6E6E",
        lightRed1: "#EB575733",
        darkRed2: "#EE6E6E33",
        lightOrange1: "#F2994A",
        darkOrange1: "#F4A662",
        lightOrange2: "#F2C94C33",
        darkOrange2: "#f4D06433",
        lightOrange3: "#FCF4DB",
        darkOrange3: "#3C2E05",
        lightOrange4: "#FF7C04",
        darkOrange4: "#FF8B1E",
        lightAsh1: "#DDE1E438",
        darkAsh1: "#262C3038",
        lightAsh2: "#F8F8F9",
        lightAsh3: "#00000066",
        darkAsh3: "#FFFFFF66",
        lightAsh4: "#0000001A",
        darkAsh4: "#FFFFFF1A",
        lightAsh5: "##0000000D",
        darkAsh5: "#FFFFFF0D",
        lightAsh6: "#F9F9FA",
        darkAsh6: "#121212",
        ashColor1: "#626D7D",
        ashColor2: "#5E6E78",
        grayColor: "#E0E0E0",
        blackColor: "#1F1F1F"
      },
      boxShadow: {
        header: '0px -9px 43px 0px #1c1c1c',
        form:'0px 0px 12px 0px #1e248154'
      },
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [ flowbite.plugin(),],
}

