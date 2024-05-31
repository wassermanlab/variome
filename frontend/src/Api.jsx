
import _ from 'lodash';

import config from './config.json';
const API_URL_BASE = config.backend_url;//'http://127.0.0.1:8000/api/';

var map = {};

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    let cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      let cookie = _.trim(cookies[i]);
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

var csrftoken;

function cachedFetch(url, query, method = 'GET', data) {

  // NOTE: in settings.py CSRF_COOKIE_HTTPONLY = True blocks getting csrftoken from the cookie
  // we only need it for POST requests

  var params = new URLSearchParams(query);
  if (params.toString()) {
    url += '?' + params.toString();
  }
  var key = url;
  //  console.log('cr', key);
  if (!map[key]) {
    //    console.log('new', key);
    var options = {
      credentials: 'include',
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      //      cors: 'no-cors',
      body: data ? JSON.stringify(data) : null,
    };

    if (_.isString(csrftoken)) {
      //      console.log('set csrftoken', csrftoken);
      options.headers['X-Csrftoken'] = csrftoken;
    }

    map[key] = fetch(url, options)
      .then(response => {

        map[key] = null;

        if (response.status >= 200 && response.status < 300) {
          return response.json();
        } else {
          throw response;
        }
      })
      .then((json) => {
        if (_.isString(_.get(json, 'user.csrf_token'))) {
          //          console.log('saving csrf token', json.user.csrf_token);
          csrftoken = json.user.csrf_token;
        }
        map[key] = null;
        /*
        // uncomment for fake loading time
        return new Promise((resolve, reject) => {
          setTimeout(() => {
            resolve(response.json());
          }, 2000);
        });*/
        return json;//response.json();
      });
  }
  return map[key];
}

const Api = {
  get: async (path, query) => {
    try {
      var json = await cachedFetch(API_URL_BASE + path, query);
//      console.log('api get', path, query, json)
    } catch (response) {
      return Promise.reject(response);
    }
    return json;
  },
  post: async (path, data, query) => {
    try {
      return cachedFetch(config.backend_root + path, query, 'POST', data);
    } catch ({ error, status, response }) {
      // ... i don't think this gets run (catches are in the fetch call above)
      console.error('Error fetching ' + path, error);
      return { errors: ["something went wrong"] };
    }
  }
}


export default Api