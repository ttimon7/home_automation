import { convertRemToPixels, vh, vw } from '../../utils/funcUtils';
import style from './Slider.module.css'

export enum Orientation {
    HORIZONTAL = 1,
    VERTICAL,
}

const getTrackShadowOffset = (orientation: Orientation, value: number) => {
    // const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
    // const vh = Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0);
    // Based on values set through style
    //   * horizontal: .sliderHorizontal input > width
    //   * vertical: .sliderVertical input > width
    const horizontalWidth = Math.min(0.7 * vw(), 0.6 * vh()) - 0.03 * vw() - convertRemToPixels(1.1);
    const verticalWidth = Math.min(0.7 * vw(), 0.6 * vh());
    const base = orientation === Orientation.VERTICAL ? verticalWidth : horizontalWidth

    return ((value / 255) * base)
}

export const Slider = ({min, max, name, orientation, colors, handler, value = 0}: {min: number, max: number, name: string, orientation: Orientation, colors: [string, string?], handler: Function, value?: number}) => {
    const trackShadowOffset = getTrackShadowOffset(orientation, value)

    const styles = colors.length === 1 ? {
        boxShadow: `inset 0 0 5px 1px black, inset ${trackShadowOffset}px 0 0 0 #${colors[0]}`
    } : {
        boxShadow: `inset 0 0 5px 1px black, inset ${trackShadowOffset}px 0 0 0 #${colors[0]}, inset -2000px 0 0 0 #${colors[1]}`
    }

    const updateTrackColor = (event: React.ChangeEvent<HTMLInputElement>) => {
        handler(Number(event.target.value));
    }

    return <div className={orientation === Orientation.VERTICAL ? style.sliderVertical : style.sliderHorizontal}>
        <div className={style.sliderWrapper}>
            {(orientation === Orientation.HORIZONTAL) && <div className={`${style.sliderLabel} ${style.sliderLabelHorizontal}`}>{name}</div>}
            <input
                className={style.sliderBar}
                type="range"
                min={min}
                max={max}
                list="ticks"
                value={value} /* If a fixed value is set the thumb is not moving */
                onInput={updateTrackColor}
                style={styles}
                />
            {(orientation === Orientation.VERTICAL) && <div className={`${style.sliderLabel} ${style.sliderLabelVertical}`}>{name}</div>}
        </div>
    </div>
}
