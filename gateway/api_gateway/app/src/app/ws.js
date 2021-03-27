import {showMessage} from './actionCreators';
import {store} from "./store";
import {ADD_NEW} from './actions';


const dispatch = action => {
  store.dispatch(action);
};

export const createFeedWebsocket = async () => {
  let ws;
  return new Promise((resolve, reject) => {
    try {
      ws = new WebSocket(`ws://${window.location.host}/api/v1/news/ws`);
    } catch (e) {
      reject(e);
    }
    ws.onmessage = (e) => {
      dispatch({type: ADD_NEW, payload: JSON.parse(e.data)});
    };
    ws.onclose = () => {
    };
    ws.onerror = () => {
      dispatch(showMessage("Unexpected websocket error"))
    };
    ws.onopen = () => {
      resolve(ws);
      const state = store.getState();
      const authentication = state.userData.authentication;
      ws.send(JSON.stringify(authentication));
    };
  })
}
