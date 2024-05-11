import { useEffect, useState } from 'react'

import { Button } from '../Button/Button'
import { Orientation, Slider } from '../Slider/Slider'
import partial from '../../utils/funcUtils'
import { RgbState, RgbStateName } from '../../types/colorTypes'
import style from './Dashboard.module.css'
import syncRgbwState from '../../actions/syncState'
import togglePower from '../../actions/togglePower'
import saveRgbwState from '../../actions/saveState'

// Even though the linter reports an error, these imports are correct.
// They work thanks to the `vite-plugin-svgr` plugin.
// @ts-ignore: 2307
import Light from '../../assets/light_bulb_2.svg?react'
// @ts-ignore: 2307
import Floppy from '../../assets/floppy_disk.svg?react'
// @ts-ignore: 2307
import OnOff from '../../assets/on-off_sign.svg?react'


const LOCAL_STORAGE_KEY = "colors"
const DEFAULT_COLORS = {
    "red": 0,
    "green": 0,
    "blue": 0,
    "white": 55,
}

const getDefaultRgbState = () : RgbState => {
    const fallbackMessage = "Falling back to default RGB state."

    let rgbState = DEFAULT_COLORS
    try {
        const rawColors = localStorage.getItem(LOCAL_STORAGE_KEY);
        if (rawColors !== null) {
            rgbState = JSON.parse(rawColors);
            console.log(`Saved RGB state found.`)
        } else {
            console.log(`No saved RGB state found. ${fallbackMessage}`);
        }
    }
    catch(err) {
        console.log(`Failed to parse saved RGB state. ${fallbackMessage}`);
    }

    return rgbState;
}

const Dashboard = ({}: {}) => {
    const [colors, setRgbState] = useState<RgbState>(getDefaultRgbState())

    const setColor = (color: RgbStateName, amount: number) => {
        let obj: RgbState = {}
        obj[color] = amount
        setRgbState({
            ...colors,
            ...obj
        });
    }

    const setColorRed = partial(setColor, ["red"])
    const setColorGreen = partial(setColor, ["green"])
    const setColorBlue = partial(setColor, ["blue"])
    const setColorWhite = partial(setColor, ["white"])
    const syncData = partial(syncRgbwState, [colors])

    useEffect(() => {
        console.log(`colors: ${JSON.stringify(colors)}`)

        localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(colors));
    }, [colors])

    return <div className={style.dashboard}>
        <div className={style.rgbSection}>
            <Slider name="R" min={0} max={255} orientation={Orientation.VERTICAL} colors={["ff1a00"]} handler={setColorRed} value={colors.red}></Slider>
            <Slider name="G" min={0} max={255} orientation={Orientation.VERTICAL} colors={["00ff97"]} handler={setColorGreen} value={colors.green}></Slider>
            <Slider name="B" min={0} max={255} orientation={Orientation.VERTICAL} colors={["0080ff"]} handler={setColorBlue} value={colors.blue}></Slider>
        </div>
        <div className={style.wSection}>
            <Slider name="W" min={0} max={255} orientation={Orientation.HORIZONTAL} colors={["fffeca"]} handler={setColorWhite} value={colors.white}></Slider>
        </div>
        <div className={style.bSection}>
            <Button image={<Floppy />} handler={saveRgbwState}></Button>
            <Button image={<Light />} isBig={true} handler={syncData}></Button>
            <Button image={<OnOff />} handler={togglePower}></Button>
        </div>
    </div>
}

export default Dashboard
