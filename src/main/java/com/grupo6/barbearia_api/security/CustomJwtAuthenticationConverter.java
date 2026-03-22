package com.grupo6.barbearia_api.security;

import org.springframework.core.convert.converter.Converter;
import org.springframework.security.authentication.AbstractAuthenticationToken;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationConverter;
import org.springframework.stereotype.Component;

import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@Component
public class CustomJwtAuthenticationConverter implements  Converter<Jwt, AbstractAuthenticationToken> {
    private final JwtAuthenticationConverter jwtAuthenticationConverter;

    public CustomJwtAuthenticationConverter() {
        this.jwtAuthenticationConverter = new JwtAuthenticationConverter();
        this.jwtAuthenticationConverter.setJwtGrantedAuthoritiesConverter(this::extractAuthorities);
        this.jwtAuthenticationConverter.setPrincipalClaimName("sub");
    }

    @Override
    public AbstractAuthenticationToken convert(Jwt jwt) {
        return jwtAuthenticationConverter.convert(jwt);
    }

    private Collection<GrantedAuthority> extractAuthorities(Jwt jwt) {
        List<String> permissions = jwt.getClaimAsStringList("permissions");

        if (permissions == null || permissions.isEmpty()) {
            return Collections.emptyList();
        }

        return permissions.stream()
                .map(permission -> "ROLE_" + permission.toUpperCase().replace(":", "_"))
                .map(SimpleGrantedAuthority::new)
                .collect(Collectors.toList());
    }
}

