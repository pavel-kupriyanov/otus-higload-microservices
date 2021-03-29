import {TextField, FormControl, InputLabel, Select, MenuItem} from "@material-ui/core";


export function SimpleField(
  {
    input: {name, onChange, value, ...restInput},
    meta, submitError, style, ...rest
  }) {
  const s = style ? style : {};
  return <TextField
    {...rest}
    name={name}
    helperText={meta.touched ? meta.error || submitError : undefined}
    error={(meta.error || submitError) && meta.touched}
    inputProps={restInput}
    onChange={onChange}
    value={value}
    style={{margin: 10, minWidth: '60%', ...s}}
    id="outlined-basic"
    variant="outlined"
  />
}


export function SimpleSelect(
  {
    input: {name, onChange, value, ...restInput},
    meta, submitError, label, options, ...rest
  }) {
  return <FormControl variant="outlined" style={{margin: 10, minWidth: '60%'}}>
    <InputLabel id="demo-simple-select-outlined-label">{label}</InputLabel>
    <Select
      {...rest}
      name={name}
      helperText={meta.touched ? meta.error || submitError : undefined}
      error={(meta.error || submitError) && meta.touched}
      inputProps={restInput}
      labelId="demo-simple-select-outlined-label"
      id="demo-simple-select-outlined"
      value={value}
      onChange={onChange}
      label={label}
    >
      {Object.keys(options).map(option =>
        <MenuItem key={"select" + option} value={option}>
          {options[option]}
        </MenuItem>)}
    </Select>
  </FormControl>

}
