const TOKEN_FIELD_NAME = 'ACCESS_TOKEN';
export const REQUEST_STATUSES = {
  WAITING: 'WAITING',
  DECLINED: 'DECLINED',
}

// TODO: ADD PAGINATE LATER

export const parsePayloadError = response => {
  const errors = {};
  response.data.detail.forEach(item => {
    const name = item.loc[item.loc.length - 1];
    errors[name] = item.msg;
  });
  return errors;
}


export const storeTokenIntoStorage = token => {
  localStorage.setItem(TOKEN_FIELD_NAME, JSON.stringify(token));
}

export const loadTokenFromStorage = () => {
  const token = localStorage.getItem(TOKEN_FIELD_NAME);
  if (!token) {
    return null;
  }
  const parsedToken = JSON.parse(token);
  if (parsedToken.expired_at < new Date().getTime() / 1000) {
    return null;
  }
  return parsedToken;
};

export const deleteTokenFromStorage = () => {
  localStorage.removeItem(TOKEN_FIELD_NAME);
}


export const arrayToQueryString = (name, arr) => {
  const encodedName = encodeURIComponent(name);
  const str = arr.map(item => `${encodedName}=${encodeURIComponent(item)}`);
  return str.join("&");
}

export const toQueryString = obj => {
  const str = Object.keys(obj).map(key => {
    return encodeURIComponent(key) + "=" + encodeURIComponent(obj[key])
  })

  return str.join("&");
}


export const prepareMessages = (oldMessages, newMessages) => {
  const alreadyAddedIds = oldMessages.map(m => m.id);
  const messages = Array.from(oldMessages);
  newMessages.forEach(m => {
    if (alreadyAddedIds.includes(m.id)) {
      return
    }
    alreadyAddedIds.push(m.id);
    messages.push(m);
  })
  return messages.sort((a, b) => {return a.created < b.created ? -1 : 1})
}
