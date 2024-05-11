import { ReactNode } from 'react'
import style from './Button.module.css'


export const Button = ({text=undefined, image=undefined, isBig=false, latching=true, handler}: {text?: string, image?: ReactNode, isBig?: boolean, latching?: boolean, handler?: Function}) => {
    // Dynamically setting CSS variables by shadowing presets
    // See: <https://stackoverflow.com/questions/41503150/adding-style-attributes-to-a-css-class-dynamically-in-react-app>
    const styles={ ['--light-color' as any]: `rgba(250, 180, 250, 1.0)` }

    const handleOnPress = (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => {
        if (handler) {
            handler();
        } else {
            console.log(event.detail)
        }
    }

    return <div className={style.buttonWrapperRound} style={styles}>
        <button
            className={`${style.buttonRound} ${isBig ? style.buttonBig : style.buttonSmall}`}
            onClick={handleOnPress}>
            {text === undefined ? image : <div className={style.buttonTextWrapper}>{text}</div>}
        </button>
    </div>
}
