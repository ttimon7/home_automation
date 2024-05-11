import config from '../appConfig'

const togglePower = () => {
    const url = `${config.server_base_url}/api/power`;
    const method = "POST";

    fetch(url, {
        method: method
        // mode: "no-cors",  // remove for production
    })
    .then(response => console.log(response.status));
};

export default togglePower;
