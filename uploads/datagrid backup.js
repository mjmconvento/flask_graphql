export default createFragmentContainer(
  InboxDataGrid,
  graphql`
    fragment InboxDataGrid_message on Messages {
      id
      message
    }
  `
);