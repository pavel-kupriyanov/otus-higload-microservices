import React from 'react';
import {connect} from "react-redux";
import {bindActionCreators} from "redux";
import {animateScroll} from "react-scroll";

import {
  getChatUser,
  clearChatUser,
  getMessages,
  clearMessages,
  sendMessage
} from "../../../app/actionCreators";

import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Divider from '@material-ui/core/Divider';
import List from '@material-ui/core/List';

import {Form} from "react-final-form";

import Message from "./Message";
import MessageForm from "./Form";
import {Button} from "@material-ui/core";

const PAGE_LIMIT = 100;


const chatStyle = {
  width: '100%',
  height: '70vh',
  marginTop: 10,
  minWidth: 650,
  overflowY: 'auto'
}


class ChatPage extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      page: 1,
      isAll: false,
    }
    this.handleSubmit = this.handleSubmit.bind(this);
    this.scrollToBottom = this.scrollToBottom.bind(this);
    this.handleOlder = this.handleOlder.bind(this);
  }


  componentDidMount() {
    const {getMessages, getChatUser, chatUserId} = this.props;
    getChatUser(chatUserId);
    getMessages(chatUserId, 0, 1, PAGE_LIMIT);

    this.interval = setInterval(() => {
      const messages = this.props.chat.messages;
      const lastMessage = messages[messages.length - 1];
      if (lastMessage) {
        getMessages(chatUserId, lastMessage.created, 1, PAGE_LIMIT);
      }
    }, 2 * 1000);
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    const prevMessages = prevProps.chat.messages;
    const messages = this.props.chat.messages;

    const lastPrevMessage = prevMessages[prevMessages.length - 1];
    const lastMessage = messages[messages.length - 1];

    if (lastPrevMessage !== lastMessage) {
      this.scrollToBottom();
    }
  }

  componentWillUnmount() {
    const {clearChatUser, clearMessages} = this.props;
    clearChatUser();
    clearMessages();
    clearInterval(this.interval);
  }

  scrollToBottom() {
    animateScroll.scrollToBottom({containerId: "scroll-end", duration: 0});
  }

  handleSubmit(form) {
    const {sendMessage, chatUserId} = this.props;
    sendMessage(chatUserId, form.text);
  }

  async handleOlder(page) {
    const {getMessages, chatUserId} = this.props;
    const isNotEmpty = await getMessages(chatUserId, 0, page, PAGE_LIMIT);
    this.setState({...this.state, page: page, isAll: !isNotEmpty});
  }

  render() {

    const {chat, currentUser} = this.props;
    const {page, isAll} = this.state;
    const users = [chat.user, currentUser];
    const isReady = chat.user.id && currentUser.id;
    return (
      <>
        <Grid container component={Paper} style={chatStyle} id="scroll-end">
          <Grid item xs={12}>
            <List>
              {!isAll && <Button
                variant="contained"
                color="primary"
                type="submit"
                size="small"
                style={{marginLeft: '10px'}}
                onClick={() => this.handleOlder(page + 1)}>
                Older messages
              </Button>}
              {isReady && chat.messages.map(m =>
                <Message user={users.find(u => u.id === m.author_id)} message={m} key={m.id}/>)}
            </List>
            <Divider/>
          </Grid>
        </Grid>
        <Form onSubmit={this.handleSubmit} component={MessageForm}/>
      </>
    );
  }
}

const mapStateToProps = state => ({
  chat: state.chat,
  currentUser: state.userData.user
});

const mapDispatchToProps = dispatch => {
  return bindActionCreators({
    getChatUser, clearChatUser, getMessages, clearMessages, sendMessage
  }, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(ChatPage);
