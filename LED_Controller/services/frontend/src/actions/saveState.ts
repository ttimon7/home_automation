import config from '../appConfig'

const saveRgbwState = () => {
    const url = `${config.server_base_url}/api/color/save`;
    const method = "POST";

    fetch(url, {
        method: method
        // mode: "no-cors",  // remove for production
    })
    .then(response => console.log(response.status));
};

export default saveRgbwState;
