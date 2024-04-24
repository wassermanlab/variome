
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


function cachedFetch(url, query, method='GET', data) {

  // NOTE: in settings.py CSRF_COOKIE_HTTPONLY = True blocks getting csrftoken this way
  // we only need it for POST requests
  var csrftoken = getCookie('csrftoken');

  var params = new URLSearchParams(query);
  if (params.toString()) {
    url += '?' + params.toString();
  }
  var key = url;
  //  console.log('cr', key);
  if (!map[key]) {
    //    console.log('new', key);
    map[key] = fetch(url, {
      credentials: 'include',
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
//      cors: 'no-cors',
      body: data ? JSON.stringify(data) : null,
    })
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
    },
    post: async (path, data, query) => {
        try {
            return cachedFetch(API_URL_BASE + path, query, 'POST', data);
        } catch (error) {
            console.error('Error fetching '+path, error);
            return {errors:["something went wrong"]};
        }
    }
}


export default Api