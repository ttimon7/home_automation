import config from '../appConfig'
import { RgbState } from '../types/colorTypes'

const syncRgbwState = ( rgbColors: RgbState ) => {
    const url = `${config.server_base_url}/api/color`;
    const method = "POST";
    const body = JSON.stringify(rgbColors)

    console.log(`body: ${body}`)

    fetch(url, {
        method: method,
        // mode: "no-cors",  // remove for production
        body: body,
        headers: new Headers({
            'Content-Type': 'application/json; charset=UTF-8'
        })
    })
    .then(response => response.json())
    .then(data => console.log(data));
};

export default syncRgbwState;
