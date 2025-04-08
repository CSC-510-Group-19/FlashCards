import { Container, Col, Row } from "react-bootstrap";
import githubIcon from '../assets/images/sso/github.png';
import googleIcon from '../assets/images/sso/googleSignIn.png';
import appleIcon from '../assets/images/sso/applelogin.png';
import { signInWithProvider } from '../api/auth';

const OAuthOptions = () => {
    
  return (
    <Container className="p-1 m-1">
      <div
        className="d-flex justify-content-around align-items-center"></div>
      <Row className="alt-login-opt text-center">
      <Col xs="auto">
          <img src={githubIcon} alt="GitHub Login" style={{ height: '100px', width: '100px', cursor: 'pointer',zIndex: 1000,
    position: 'relative' }}onClick={() => alert("Hello World!")} />
        </Col>
        <Col xs="auto">
          <img src={googleIcon} alt="Google Login" style={{ height: '100px', width: '100px', cursor: 'pointer' ,zIndex: 1000,
    position: 'relative'}}onClick={() => signInWithProvider('google')} />
        </Col>
        <Col xs="auto">
          <img src={appleIcon} alt="Apple Login" style={{ height: '100px', width: '100px', cursor: 'pointer', zIndex: 1000,
    position: 'relative'}} onClick={() => signInWithProvider('apple')} />
        </Col>
      </Row>
    </Container>
  );
};

export default OAuthOptions;