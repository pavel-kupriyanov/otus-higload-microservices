import React from 'react';
import {connect} from "react-redux";
import PropTypes from "prop-types";
import {bindActionCreators} from "redux";
import {Form} from "react-final-form";
import {Container, Grid, Typography} from "@material-ui/core";


import {getUsers, clearUsers} from "../../../app/actionCreators";
import SearchForm from "./Form";
import UserCard from "../../common/components/UserCard";
import PaginateButtons from "../../common/components/PaginateButtons";

const PAGE_LIMIT = 100;


class UsersPage extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      page: 1,
      isAll: false,
      lastQuery: {
        first_name: '',
        last_name: ''
      }
    }
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handlePage = this.handlePage.bind(this);
  }

  componentDidMount() {
    this.props.getUsers('', '', 1, PAGE_LIMIT);
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    const {users} = this.props;
    if (prevProps.users.length === users.length) {
      return
    }
    const isAll = users.length < PAGE_LIMIT;
    this.setState({...this.state, isAll});
  }

  componentWillUnmount() {
    this.props.clearUsers();
  }

  handleSubmit(values) {
    this.props.getUsers(values.first_name, values.last_name, 1, PAGE_LIMIT);
    this.setState({...this.state, lastQuery: values});
  }

  handlePage(pageNum) {
    const {lastQuery} = this.state;
    this.props.getUsers(lastQuery.first_name, lastQuery.last_name, pageNum, PAGE_LIMIT);
    this.setState({...this.state, page: pageNum});
  }


  render() {
    const {users} = this.props;
    const {page, isAll} = this.state;


    return (
      <Container>
        <Form
          component={SearchForm}
          onSubmit={this.handleSubmit}
        />
        <Grid item container spacing={2} justify="space-between" direction="row">
          {users.map(user => <Grid item xs={6} key={'user_' + user.id}>
              <UserCard user={user}/>
            </Grid>
          )}
          {!users.length && <Typography variant="h5" component="h2" style={{marginBottom: "10px"}}>
            Users not found
          </Typography>}
        </Grid>
        <PaginateButtons page={page} isAll={isAll} handlePage={this.handlePage}/>
      </Container>
    );
  }
}

UsersPage.propTypes = {
  getUsers: PropTypes.func.isRequired,
  clearUsers: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  users: state.users,
});

const mapDispatchToProps = dispatch => {
  return bindActionCreators({getUsers, clearUsers}, dispatch)
}


export default connect(mapStateToProps, mapDispatchToProps)(UsersPage);
