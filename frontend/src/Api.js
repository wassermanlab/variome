
import config from './config.json';
const API_URL_BASE = config.backend_url;//'http://127.0.0.1:8000/api/';

var map = {};

function cachedFetch(url, query) {
  var params = new URLSearchParams(query);
  if (params.toString()) {
    url += '?' + params.toString();
  }
  var key = url;
  //  console.log('cr', key);
  if (!map[key]) {
    //    console.log('new', key);
    map[key] = fetch(url)
      .then((response) => {
        map[key] = null;
        /*
        // uncomment for fake loading time
        return new Promise((resolve, reject) => {
          setTimeout(() => {
            resolve(response.json());
          }, 2000);
        });*/
        return response.json();
      });
  }
  return map[key];
}

const Api = {
    get:async (path, query) => {
        try {
            return cachedFetch(API_URL_BASE + path, query);
        } catch (error) {
            console.error('Error fetching '+path, error);
            return {errors:["something went wrong"]};
        }
    }
}


export default Api