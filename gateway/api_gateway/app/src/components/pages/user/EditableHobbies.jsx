import React from 'react';
import PropTypes from "prop-types";

import {Field, Form} from "react-final-form";
import {required, SimpleField} from "../../common";
import {bindActionCreators} from "redux";
import {addHobby, deleteHobby} from "../../../app/actionCreators";
import {connect} from "react-redux";
import {Button, Chip} from "@material-ui/core";

const chipStyle = {
  marginTop: '5px',
  marginRight: '5px',
}

class EditableHobbies extends React.Component {

  constructor(props) {
    super(props);
    this.addHobby = this.addHobby.bind(this);
  }

  addHobby(values, form) {
    this.props.addHobby(values.hobby);
    setTimeout(() => form.restart(), 0);
  }

  deleteHobby(id) {
    this.props.deleteHobby(id);
  }

  render() {
    const {hobbies} = this.props;
    const alreadyAdded = value => hobbies.find(hobby => hobby.name === value) ? 'Already added' : null;
    const composeValidators = (...validators) => value =>
      validators.reduce((error, validator) => error || validator(value), undefined)


    return (
      <div>
        {hobbies.map(hobby => {
          return <Chip
            key={'hobby_' + hobby.id}
            label={hobby.name}
            onDelete={() => this.deleteHobby(hobby.id)}
            style={chipStyle}/>
        })}
        <Form onSubmit={this.addHobby}>
          {props => (
            <form onSubmit={props.handleSubmit} style={{marginTop: '10px'}}>
              <Field name="hobby" validate={composeValidators(alreadyAdded, required)} type="text">
                {({input, meta}) => {
                  return <SimpleField
                    input={input}
                    meta={meta}
                    label={"Hobby"}
                  />
                }}
              </Field>
              <Button
                style={{marginTop: '15px'}}
                variant="contained"
                color="primary"
                type="submit"
                size="large">
                Submit
              </Button>
            </form>
          )}
        </Form>
      </div>
    );
  }
}

EditableHobbies.propTypes = {
  hobbies: PropTypes.array.isRequired,
  addHobby: PropTypes.func,
  deleteHobby: PropTypes.func
}


const mapDispatchToProps = dispatch => {
  return bindActionCreators({addHobby, deleteHobby}, dispatch)
}


export default connect(null, mapDispatchToProps)(EditableHobbies);






