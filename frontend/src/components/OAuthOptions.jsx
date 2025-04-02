import {Container, Col, Row} from "react-bootstrap";

const OAuthOptions = () => {

    const GitHub = () => {
        const github = document.createElement('img')
        github.setAttribute('src', '../../images/sso/github.png')
        return github
    }
    const Google = () => {
        const google = document.createElement('img')
        google.setAttribute('src', '../../images/sso/googleSignIn.png')
        return google
    }
    const Apple = () => {
        const apple = document.createElement('img')
        apple.setAttribute('src', '../../images/sso/applelogin.png')
        return apple
    }

    return (
        <Container>
            <Row className="alt-login-opt">
                <Col>
                    <GitHub />
                </Col>
                <Col>
                    <Google />
                </Col>
                <Col>
                    <Apple />
                </Col>
            </Row>
        </Container>
    )
}

export default OAuthOptions