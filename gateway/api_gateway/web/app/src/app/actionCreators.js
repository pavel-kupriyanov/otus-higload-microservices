import {default as axiosBase} from 'axios';
import {
  LOGIN_SUCCESS,
  LOGIN_FAILED,
  SHOW_LOADER,
  SHOW_MESSAGE,
  HIDE_LOADER,
  HIDE_MESSAGE,
  REGISTER_FAILED,
  REGISTER_SUCCESS,
  GET_USER_SUCCESS,
  ADD_HOBBY_SUCCESS,
  DELETE_HOBBY_SUCCESS,
  LOGOUT,
  GET_USERS,
  CLEAR_USER,
  CLEAR_USERS,
  DELETE_FRIENDSHIP,
  ADD_FRIEND_REQUEST,
  DELETE_FRIEND_REQUEST,
  ACCEPT_FRIEND_REQUEST,
  DECLINE_FRIEND_REQUEST,
  GET_USER_DATA,
  GET_FRIEND_REQUEST_USERS,
  CLEAR_CHAT_USER,
  CLEAR_MESSAGES,
  GET_CHAT_USER,
  GET_MESSAGES,
  CLEAR_NEWS,
  GET_NEWS,
  ADD_NEW
} from "./actions";
import {
  deleteTokenFromStorage,
  storeTokenIntoStorage,
  parsePayloadError,
  toQueryString,
  arrayToQueryString
} from "./utils";
import {store} from './store';

export const HTTP_API_BASE = `http://localhost:8000/api/v1`;


const AXIOS_CONFIG = {
  timeout: 20000,
  headers: {
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json",
  },
}

const axios = axiosBase.create(AXIOS_CONFIG);

const getAuthorizedAxios = () => {
  const state = store.getState();
  const authentication = state.userData.authentication;
  const config = {
    ...AXIOS_CONFIG,
    headers: {
      ...AXIOS_CONFIG.headers,
      "X-Auth-Token": authentication && authentication.value
    }
  }
  return axiosBase.create(config)
}

const messageTimeout = 3;


export const showMessage = message => {
  return dispatch => {
    dispatch({type: SHOW_MESSAGE, payload: message});
    setTimeout(() => dispatch({type: HIDE_MESSAGE}), messageTimeout * 1000);
  }
}

export const showLoader = () => {
  return dispatch => {
    dispatch({type: SHOW_LOADER});
  }
}

export const hideLoader = () => {
  return dispatch => {
    dispatch({type: HIDE_LOADER});
  }
}

export const login = (email, password) => {
  return async dispatch => {
    dispatch(showLoader());
    let isSuccess = false;
    try {
      const response = await axios.post(`${HTTP_API_BASE}/auth/login/`, {email, password});
      isSuccess = true;
      storeTokenIntoStorage(response.data);
      dispatch({type: LOGIN_SUCCESS, payload: response.data});
    } catch (e) {
      console.log(e);
      switch (e.response.status) {
        case 422: {
          dispatch({
            type: LOGIN_FAILED,
            payload: parsePayloadError(e.response)
          });
          break;
        }
        case 400: {
          dispatch({
            type: LOGIN_FAILED,
            payload: {email: e.response.data.detail}
          });
          break;
        }
        default: {
          dispatch({
            type: LOGIN_FAILED,
            payload: {general: "Unexpected error"}
          });
        }
      }
      dispatch(showMessage("Login failed"));
    }
    dispatch(hideLoader());
    return isSuccess;
  }
}

export const logout = () => {
  return dispatch => {
    deleteTokenFromStorage();
    dispatch({type: LOGOUT})
  }
}

export const getUserData = id => {
  return async dispatch => {
    const axios = getAuthorizedAxios();
    try {
      const userPromise = axios.get(`${HTTP_API_BASE}/users/${id}/`);
      const friendsPromise = axios.get(`${HTTP_API_BASE}/users/?friends_of=${id}`);
      const friendRequestsPromise = axios.get(`${HTTP_API_BASE}/friendships/`);
      const [user, friends, friendRequests] = await Promise.all(
        [userPromise, friendsPromise, friendRequestsPromise]
      );
      dispatch({
        type: GET_USER_DATA, payload: {
          user: user.data,
          friends: friends.data || [],
          friendRequests: friendRequests.data || []
        }
      });
    } catch (e) {
      console.log(e);
      dispatch(showMessage("Auth data failed. Please reload page."));
    }
  }
}


export const register = (
  {
    email,
    password,
    first_name,
    last_name,
    age,
    gender,
    city
  }
) => {
  return async dispatch => {
    dispatch(showLoader());
    const payload = {email, password, first_name, last_name, age, gender, city};
    let isSuccess = false;
    try {
      await axios.post(`${HTTP_API_BASE}/auth/register/`, payload);
      isSuccess = true;
      dispatch(showMessage("Success!"));
      dispatch({type: REGISTER_SUCCESS});
    } catch (e) {
      console.log(e);
      dispatch(showMessage("Registration failed"));
      switch (e.response.status) {
        case 422: {
          dispatch({
            type: REGISTER_FAILED,
            payload: parsePayloadError(e.response)
          });
          break;
        }
        case 400: {
          dispatch({
            type: REGISTER_FAILED,
            payload: {email: e.response.data.detail}
          });
          break;
        }
        default: {
          dispatch({
            type: REGISTER_FAILED,
            payload: {general: "Unexpected error"}
          });
        }
      }
    }
    dispatch(hideLoader());
    return isSuccess;
  }
}


export const getUser = userId => {
  return async dispatch => {
    let isSuccess = false;
    dispatch(showLoader());
    try {
      const response = await axios.get(`${HTTP_API_BASE}/users/${userId}/`);
      isSuccess = true;
      dispatch({type: GET_USER_SUCCESS, payload: response.data});
    } catch (e) {
      console.log(e);
      dispatch(showMessage('Get user failed'))
    }
    dispatch(hideLoader());
    return isSuccess;
  }
}


export const addHobby = name => {
  return async dispatch => {
    dispatch(showLoader());
    const axios = getAuthorizedAxios();
    try {
      const createResponse = await axios.post(`${HTTP_API_BASE}/hobbies/`, {name});
      await axios.put(`${HTTP_API_BASE}/users/hobbies/${createResponse.data.id}/`);
      dispatch({type: ADD_HOBBY_SUCCESS, payload: createResponse.data});
    } catch (e) {
      console.log(e);
      dispatch(showMessage('Add hobby failed'))
    }
    dispatch(hideLoader());
  }
}

export const deleteHobby = id => {
  return async dispatch => {
    dispatch(showLoader());
    const axios = getAuthorizedAxios();
    try {
      await axios.delete(`${HTTP_API_BASE}/users/hobbies/${id}/`);
      dispatch({type: DELETE_HOBBY_SUCCESS, payload: id});
    } catch (e) {
      console.log(e);
      dispatch(showMessage('Delete hobby failed'));
    }
    dispatch(hideLoader());
  }
}

export const getFriends = id => {
  return async dispatch => {
    dispatch(showLoader());
    try {
      const response = await axios.get(`${HTTP_API_BASE}/users/?friends_of=${id}`,);
      dispatch({type: GET_USERS, payload: response.data});
    } catch (e) {
      console.log(e);
      dispatch(showMessage('Get friends failed'));
    }
    dispatch(hideLoader());
  }
}

export const clearUser = () => {
  return dispatch => {
    dispatch({type: CLEAR_USER});
  }
}

export const clearUsers = () => {
  return dispatch => {
    dispatch({type: CLEAR_USERS});
  }
}

export const getUsers = (first_name, last_name, page = 1, paginate_by = 100) => {
  return async dispatch => {
    dispatch(showLoader());
    const query = toQueryString({first_name, last_name, page, paginate_by});
    try {
      const response = await axios.get(`${HTTP_API_BASE}/users/?${query}`,);
      dispatch({type: GET_USERS, payload: response.data});
    } catch (e) {
      console.log(e);
      dispatch(showMessage('Get users failed'));
    }
    dispatch(hideLoader());
  }
}

export const deleteFriendship = id => {
  return async dispatch => {
    const axios = getAuthorizedAxios();
    dispatch(showLoader());
    try {
      await axios.delete(`${HTTP_API_BASE}/friendships/friendship/${id}/`,);
      dispatch({type: DELETE_FRIENDSHIP, payload: id});
    } catch (e) {
      console.log(e);
      dispatch(showMessage('Friendship deleting failed'));
    }
    dispatch(hideLoader());
  }
}

export const addFriendRequest = userId => {
  return async dispatch => {
    const axios = getAuthorizedAxios();
    dispatch(showLoader());
    try {
      const response = await axios.post(`${HTTP_API_BASE}/friendships/${userId}/`);
      dispatch({type: ADD_FRIEND_REQUEST, payload: response.data});
    } catch (e) {
      console.log(e);
      dispatch(showMessage('Add friend failed'));
    }
    dispatch(hideLoader());
  }
}

export const deleteFriendRequest = id => {
  return async dispatch => {
    const axios = getAuthorizedAxios();
    dispatch(showLoader());
    try {
      await axios.delete(`${HTTP_API_BASE}/friendships/${id}/`);
      dispatch({type: DELETE_FRIEND_REQUEST, payload: id});
    } catch (e) {
      console.log(e);
      dispatch(showMessage('Friend request deleting failed'));
    }
    dispatch(hideLoader());
  }
}

export const acceptFriendRequest = id => {
  return async dispatch => {
    const axios = getAuthorizedAxios();
    dispatch(showLoader());
    try {
      const response = await axios.put(`${HTTP_API_BASE}/friendships/accept/${id}/`);
      const userResponse = await axios.get(`${HTTP_API_BASE}/users/${response.data.friend_id}/`);
      dispatch({type: ACCEPT_FRIEND_REQUEST, payload: {requestId: id, friend: userResponse.data}});
    } catch (e) {
      console.log(e);
      dispatch(showMessage('Friend request accepting failed.'));
    }
    dispatch(hideLoader());
  }
}


export const declineFriendRequest = id => {
  return async dispatch => {
    const axios = getAuthorizedAxios();
    dispatch(showLoader());
    try {
      await axios.put(`${HTTP_API_BASE}/friendships/decline/${id}/`);
      dispatch({type: DECLINE_FRIEND_REQUEST, payload: id});
    } catch (e) {
      console.log(e);
      dispatch(showMessage('Friend request declining failed.'));
    }
    dispatch(hideLoader());
  }
}


export const getFriendRequestUsers = ids => {
  return async dispatch => {
    dispatch(showLoader());
    try {
      const response = await axios.get(`${HTTP_API_BASE}/users/?${arrayToQueryString('ids', ids)}`);
      dispatch({type: GET_FRIEND_REQUEST_USERS, payload: response.data});
    } catch (e) {
      console.log(e);
    }
    dispatch(hideLoader());
  }
}


export const clearChatUser = () => {
  return dispatch => dispatch({type: CLEAR_CHAT_USER});
}

export const clearMessages = () => {
  return dispatch => dispatch({type: CLEAR_MESSAGES});
}


export const getChatUser = userId => {
  return async dispatch => {
    let isSuccess = false;
    dispatch(showLoader());
    try {
      const response = await axios.get(`${HTTP_API_BASE}/users/${userId}/`);
      isSuccess = true;
      dispatch({type: GET_CHAT_USER, payload: response.data});
    } catch (e) {
      console.log(e);
      dispatch(showMessage('Get user failed'))
    }
    dispatch(hideLoader());
    return isSuccess;
  }
}

export const getMessages = (userId, afterTimestamp = 0, page = 1, pageLimit = 100) => {
  return async dispatch => {
    let data = [];
    const payload = {
      to_user_id: userId,
      after_timestamp: afterTimestamp,
      page: page,
      paginate_by: pageLimit
    }
    const query = toQueryString(payload);
    const axios = getAuthorizedAxios();
    try {
      const response = await axios.get(`${HTTP_API_BASE}/messages/?${query}`);
      data = response.data;
      dispatch({type: GET_MESSAGES, payload: data});
    } catch (e) {
      console.log(e);
      dispatch(showMessage('Get messages failed'))
    }
    return data.length > 0;
  }
}

export const sendMessage = (userId, text) => {
  return async dispatch => {
    let isSuccess = false;
    const axios = getAuthorizedAxios();
    dispatch(showLoader());
    try {
      const response = await axios.post(`${HTTP_API_BASE}/messages/`, {to_user_id: userId, text});
      isSuccess = true;
      dispatch({type: GET_MESSAGES, payload: [response.data]});
    } catch (e) {
      console.log(e);
      dispatch(showMessage('Send message failed'))
    }
    dispatch(hideLoader());
    return isSuccess;
  }
}


export const getNews = (userId, page = 1, paginate_by = 100, order='DESC') => {
  return async dispatch => {
    dispatch(showLoader());
    const query = toQueryString({page, paginate_by, order});
    try {
      const response = await axios.get(`${HTTP_API_BASE}/news/${userId}/?${query}`,);
      dispatch({type: GET_NEWS, payload: response.data});
    } catch (e) {
      console.log(e);
      dispatch(showMessage('Get news failed'));
    }
    dispatch(hideLoader());
  }
}

export const getFeed = (page = 1, paginate_by = 100, order='DESC') => {
  return async dispatch => {
    dispatch(showLoader());
    const query = toQueryString({page, paginate_by, order});
    const axios = getAuthorizedAxios();
    try {
      const response = await axios.get(`${HTTP_API_BASE}/news/feed/?${query}`,);
      dispatch({type: GET_NEWS, payload: response.data});
    } catch (e) {
      console.log(e);
      dispatch(showMessage('Get feed failed'));
    }
    dispatch(hideLoader());
  }
}

export const clearNews = () => {
  return dispatch => dispatch({type: CLEAR_NEWS});
}

export const addNew = (text) => {
    return async dispatch => {
    let isSuccess = false;
    const axios = getAuthorizedAxios();
    dispatch(showLoader());
    try {
      const response = await axios.post(`${HTTP_API_BASE}/news/`, {text});
      isSuccess = true;
      dispatch({type: ADD_NEW, payload: response.data});
    } catch (e) {
      console.log(e);
      dispatch(showMessage('Send message failed'))
    }
    dispatch(hideLoader());
    return isSuccess;
  }
}
