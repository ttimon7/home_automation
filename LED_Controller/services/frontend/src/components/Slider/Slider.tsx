import style from './Slider.module.css'

const TRACK_VALUE_OFFSET = 15

export enum Orientation {
    HORIZONTAL = 1,
    VERTICAL,
}

const getTrackShadowOffset = (value: number) => value + TRACK_VALUE_OFFSET

export const Slider = ({min, max, name, orientation, colors, handler, value = 0}: {min: number, max: number, name: string, orientation: Orientation, colors: [string, string?], handler: Function, value?: number}) => {
    const trackShadowOffset = getTrackShadowOffset(value)

    const styles = colors.length === 1 ? {
        boxShadow: `inset 0 0 5px 1px black, inset ${trackShadowOffset}px 0 0 0 #${colors[0]}`
    } : {
        boxShadow: `inset 0 0 5px 1px black, inset ${trackShadowOffset}px 0 0 0 #${colors[0]}, inset -2000px 0 0 0 #${colors[1]}`
    }

    const updateTrackColor = (event: React.ChangeEvent<HTMLInputElement>) => {
        handler(Number(event.target.value));
    }

    return <div className={orientation === Orientation.VERTICAL ? style.sliderVertical : style.sliderHorizontal}>
        <div className={style.sliderLabel}>{name}</div>
        <div className={style.sliderWrapper}>
            <input
                className={`${style.sliderBar} ${orientation === Orientation.VERTICAL ? style.vertical : ""}`}
                type="range"
                min={min}
                max={max}
                list="ticks"
                value={value} /* If a fixed value is set the thumb is not moving */
                onInput={updateTrackColor}
                style={styles}
                />
        </div>
    </div>
}
