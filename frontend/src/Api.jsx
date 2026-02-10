
import _ from 'lodash';

import Constants from './Constants';

var urlObj = new URL(import.meta.env.API_PATH, import.meta.env.BACKEND_ROOT);
const API_URL_BASE = urlObj.toString();
//const API_URL_BASE = import.meta.env.BACKEND_URL;//'http://127.0.0.1:8000/api/';

var map = {};

/*
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
}*/

var csrftoken;

function cachedFetch(url, query, method = 'GET', data, includeCredentials = true) {

  // NOTE: in settings.py CSRF_COOKIE_HTTPONLY = True blocks getting csrftoken from the cookie
  // we only need it for POST requests

  if (query){
    var params = new URLSearchParams(query);
    if (params.toString()) {
      url += '?' + params.toString();
    }
  }
  var key = url;
  //  console.log('cr', key);
  if (!map[key]) {
    //    console.log('new', key);
    var options = {
      credentials: includeCredentials ? 'include' : 'omit',
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      //      cors: 'no-cors',
      body: data ? JSON.stringify(data) : null,
    };

    if (_.isString(csrftoken) && includeCredentials) {
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

function getFetch(url){
  return cachedFetch(url, null, 'GET', null, false);
}

const Api = {
  get: async (path, query) => {
    var json;
    try {
      json = await cachedFetch(API_URL_BASE + path, query);
      //      console.log('api get', path, query, json)
    } catch (response) {
      // BW note: it would be nice to still be able to read the response body
      // for server-provided error messages even if fetch fails
      return Promise.reject(response);
    }
    return json;
  },
  gnomadGraphQLRequest: async (query, variables) => {
    var json;
      try {
        json = await cachedFetch("https://gnomad.broadinstitute.org/api",
          null,
          'POST',
          {
            query,
            variables
          },
          false
        );
      } catch (response) {
        return Promise.reject(response);
      }
      return json;
    },
    ensemblRefCheck: async (position, assemblyVersion) => {
      var json;
      var coordSystemVersion = Constants.assemblyVersions[assemblyVersion];

      if (_.isString(coordSystemVersion) && !_.isEmpty(coordSystemVersion)){
        try {
          json = await getFetch(`https://rest.ensembl.org/sequence/region/human/X:${position}..${position}:1?content-type=application/json;coord_system_version=${coordSystemVersion}`);
        } catch (response) {
          return Promise.reject(response);
        }
        return json;
      } else {
        return Promise.reject({ error: `Unsupported assembly version: ${assemblyVersion}. use "1" or "2". (2 is GRCh38)` });
      }
      
    }/*,
  post: async (path, data, query) => {
    try {
      return cachedFetch(import.meta.env.BACKEND_ROOT + path, query, 'POST', data);
    } catch ({ error, status, response }) {
      // ... i don't think this gets run (catches are in the fetch call above)
      console.error('Error fetching ' + path, error);
      return { errors: ["something went wrong"] };
    }
  }*/
}


export default Api