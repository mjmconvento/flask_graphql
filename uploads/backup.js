import * as React from 'react'
import { render } from 'react-dom'
import ApolloClient from 'apollo-client'
import { HttpLink, InMemoryCache } from 'apollo-client-preset'
import { ApolloProvider, graphql } from 'react-apollo'
import gql from 'graphql-tag'
 
// Apollo client
const client = new ApolloClient({
  	link: new HttpLink({ uri: 'http://127.0.0.1:8000/graphql' }),
  	cache: new InMemoryCache().restore({})
})
 
const POST_QUERY = gql`
{
	allPosts {
		id,
		imageUrl,
		description
	}
}
`
 
const App = graphql(POST_QUERY)(({ data }) => {
  	const { loading, Movie } = data
  	if (loading) return <div>loading...</div>
  
  	return (
		data.allPosts.map(function(post, idx) {
		   	return (
		       <p key={post.id}>{idx} {post.description}</p>
		   	)
		})
  	)

})
 
const ApolloApp = (


  	<ApolloProvider client={client}>
    	<App />
  	</ApolloProvider>
)
 
render(ApolloApp, document.getElementById('root'))